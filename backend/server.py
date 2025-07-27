from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import jwt
from datetime import datetime, timedelta
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
import hashlib
from passlib.context import CryptContext
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'nexora-bank-secure-jwt-secret-key-2025-v1.0')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()

# Create the main app without a prefix
app = FastAPI(title="Nexora Bank API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class TransactionType(str, Enum):
    TRANSFER = "transfer"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    INVESTMENT = "investment"
    LOAN_DISBURSEMENT = "loan_disbursement"
    LOAN_PAYMENT = "loan_payment"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class InvestmentType(str, Enum):
    MUTUAL_FUND = "mutual_fund"
    FIXED_DEPOSIT = "fixed_deposit"
    EQUITY = "equity"
    BONDS = "bonds"
    GOLD = "gold"

class LoanType(str, Enum):
    PERSONAL = "personal"
    HOME = "home"
    CAR = "car"
    EDUCATION = "education"
    BUSINESS = "business"

class LoanStatus(str, Enum):
    APPLIED = "applied"
    APPROVED = "approved"
    DISBURSED = "disbursed"
    REJECTED = "rejected"

# User Models
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str
    account_type: str = "savings"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    full_name: str
    email: str
    phone: str
    account_number: str = Field(default_factory=lambda: f"NEX{str(uuid.uuid4())[:8].upper()}")
    account_type: str
    balance: float = 10000.0  # Starting balance
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    phone: str
    account_number: str
    account_type: str
    balance: float
    is_active: bool

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Transaction Models
class TransactionCreate(BaseModel):
    recipient_account: str
    amount: float
    description: str = ""
    transaction_type: TransactionType = TransactionType.TRANSFER

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_account: str
    recipient_account: str
    amount: float
    description: str
    transaction_type: TransactionType
    status: TransactionStatus = TransactionStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class TransactionResponse(BaseModel):
    id: str
    sender_account: str
    recipient_account: str
    amount: float
    description: str
    transaction_type: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

# Investment Models
class InvestmentCreate(BaseModel):
    investment_type: InvestmentType
    amount: float
    duration_months: int = 12

class Investment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    investment_type: InvestmentType
    amount: float
    current_value: float
    expected_return: float
    duration_months: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    maturity_date: datetime

class InvestmentResponse(BaseModel):
    id: str
    investment_type: str
    amount: float
    current_value: float
    expected_return: float
    duration_months: int
    created_at: datetime
    maturity_date: datetime

# Loan Models
class LoanApplication(BaseModel):
    loan_type: LoanType
    amount: float
    purpose: str
    duration_months: int
    monthly_income: float

class Loan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    loan_type: LoanType
    amount: float
    purpose: str
    duration_months: int
    monthly_income: float
    interest_rate: float = 8.5
    emi: float
    status: LoanStatus = LoanStatus.APPLIED
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None

class LoanResponse(BaseModel):
    id: str
    loan_type: str
    amount: float
    purpose: str
    duration_months: int
    interest_rate: float
    emi: float
    status: str
    applied_at: datetime
    approved_at: Optional[datetime]

# Chat Models
class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    message: str
    response: str
    category: str = "general"  # general, loan, investment
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChatMessageCreate(BaseModel):
    message: str
    category: str = "general"

class ChatMessageResponse(BaseModel):
    id: str
    message: str
    response: str
    category: str
    created_at: datetime

# Utility functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def calculate_emi(principal: float, rate: float, tenure: int) -> float:
    """Calculate EMI using the standard formula"""
    monthly_rate = rate / (12 * 100)
    emi = (principal * monthly_rate * (1 + monthly_rate)**tenure) / ((1 + monthly_rate)**tenure - 1)
    return round(emi, 2)

def calculate_investment_return(amount: float, investment_type: InvestmentType, duration_months: int) -> tuple:
    """Calculate expected returns based on investment type"""
    rates = {
        InvestmentType.MUTUAL_FUND: 12.0,
        InvestmentType.FIXED_DEPOSIT: 6.5,
        InvestmentType.EQUITY: 15.0,
        InvestmentType.BONDS: 7.5,
        InvestmentType.GOLD: 8.0
    }
    
    annual_rate = rates.get(investment_type, 8.0)
    monthly_rate = annual_rate / (12 * 100)
    expected_value = amount * (1 + monthly_rate)**duration_months
    return round(expected_value, 2), round(expected_value - amount, 2)

def get_chat_response(message: str, category: str) -> str:
    """Generate chat responses based on category and message"""
    responses = {
        "loan": {
            "home loan": "🏠 Home Loan: We offer attractive home loans starting from 8.5% interest rate with up to 30 years tenure. You can borrow up to 80% of property value. Would you like to apply?",
            "personal loan": "💳 Personal Loan: Get instant personal loans up to ₹20 lakhs at 10.5% interest rate. No collateral required. Processing time: 24 hours.",
            "car loan": "🚗 Car Loan: Finance your dream car with our car loans at 9.5% interest rate. Up to 100% financing available with flexible EMI options.",
            "education loan": "🎓 Education Loan: Invest in your future with education loans up to ₹50 lakhs. Special rates for premier institutions. Moratorium period available.",
            "business loan": "🏢 Business Loan: Grow your business with our business loans up to ₹1 crore. Competitive rates starting from 11% with quick processing.",
            "default": "💰 We offer various loan options: Home Loans (8.5%), Personal Loans (10.5%), Car Loans (9.5%), Education Loans (8%), and Business Loans (11%). Which one interests you?"
        },
        "investment": {
            "mutual fund": "📈 Mutual Funds: Invest in our curated mutual fund portfolio with expected returns of 12% annually. SIP starting from ₹500/month.",
            "fixed deposit": "🏦 Fixed Deposits: Secure your money with guaranteed returns of 6.5% per annum. Tenure from 1 to 5 years available.",
            "equity": "📊 Equity Investment: Direct equity investment with potential returns up to 15%. Professional advisory services included.",
            "bonds": "💎 Government Bonds: Safe investment option with 7.5% returns. Tax benefits available under 80C.",
            "gold": "🥇 Digital Gold: Invest in 24K digital gold with easy buying/selling. Expected returns around 8% annually.",
            "default": "💎 Investment Options: Mutual Funds (12%), Fixed Deposits (6.5%), Equity (15%), Bonds (7.5%), Digital Gold (8%). What suits your risk profile?"
        },
        "general": {
            "balance": "Your current account balance and transaction history can be viewed from the dashboard. Is there anything specific you'd like to know?",
            "transfer": "You can transfer money instantly to any bank account using our secure transfer system. Daily limit is ₹2 lakhs.",
            "support": "I'm here to help you with banking, loans, and investments. Feel free to ask about any of our services!",
            "default": "Hello! I'm your Nexora Bank assistant. I can help you with account queries, loan information, investment advice, and general banking services. How may I assist you today?"
        }
    }
    
    message_lower = message.lower()
    category_responses = responses.get(category, responses["general"])
    
    for key, response in category_responses.items():
        if key in message_lower and key != "default":
            return response
    
    return category_responses["default"]

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials", 
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user_doc = await db.users.find_one({"id": user_id})
    if user_doc is None:
        raise credentials_exception
    
    return User(**user_doc)

# Auth Routes
@api_router.post("/auth/register", response_model=TokenResponse)
async def register_user(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user - convert to dict and add hashed password
    user_dict = user_data.dict()
    hashed_password = hash_password(user_data.password)
    user_dict["password"] = hashed_password
    
    # Create User object (this will add default fields like id, account_number, etc.)
    user_obj = User(**user_dict)
    
    # Prepare document for database (include password)
    user_doc = user_obj.dict()
    user_doc["password"] = hashed_password  # Ensure password is in the document
    
    # Save to database
    await db.users.insert_one(user_doc)
    
    # Create access token
    access_token = create_access_token(data={"sub": user_obj.id})
    
    # Return response (without password)
    user_response = UserResponse(**user_obj.dict())
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login_user(user_credentials: UserLogin):
    # Find user - get raw document with password
    user_doc = await db.users.find_one({"email": user_credentials.email})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password using the raw document
    if not verify_password(user_credentials.password, user_doc["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user_doc["id"]})
    
    # Return response (create User object without password for response)
    user_response = UserResponse(**user_doc)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(**current_user.dict())

@api_router.post("/auth/logout")
async def logout_user():
    return {"message": "Successfully logged out"}

# Dashboard Routes
@api_router.get("/dashboard/summary")
async def get_dashboard_summary(current_user: User = Depends(get_current_user)):
    # Get recent transactions
    recent_transactions = await db.transactions.find(
        {"$or": [{"sender_account": current_user.account_number}, {"recipient_account": current_user.account_number}]}
    ).sort("created_at", -1).limit(5).to_list(5)
    
    # Get investments
    investments = await db.investments.find({"user_id": current_user.id}).to_list(10)
    total_investments = sum([inv["amount"] for inv in investments])
    
    # Get loans
    loans = await db.loans.find({"user_id": current_user.id}).to_list(10)
    total_loans = sum([loan["amount"] for loan in loans if loan["status"] == "disbursed"])
    
    return {
        "account_number": current_user.account_number,
        "balance": current_user.balance,
        "account_type": current_user.account_type,
        "user_name": current_user.full_name,
        "total_investments": total_investments,
        "total_loans": total_loans,
        "recent_transactions_count": len(recent_transactions)
    }

# Transaction Routes
@api_router.post("/transactions/transfer", response_model=TransactionResponse)
async def transfer_money(transaction_data: TransactionCreate, current_user: User = Depends(get_current_user)):
    # Validate recipient account
    recipient = await db.users.find_one({"account_number": transaction_data.recipient_account})
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient account not found"
        )
    
    # Check if sender has sufficient balance
    if current_user.balance < transaction_data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance"
        )
    
    # Create transaction
    transaction = Transaction(
        sender_account=current_user.account_number,
        recipient_account=transaction_data.recipient_account,
        amount=transaction_data.amount,
        description=transaction_data.description,
        transaction_type=transaction_data.transaction_type,
        status=TransactionStatus.COMPLETED,
        completed_at=datetime.utcnow()
    )
    
    # Update balances
    await db.users.update_one(
        {"id": current_user.id},
        {"$inc": {"balance": -transaction_data.amount}}
    )
    
    await db.users.update_one(
        {"account_number": transaction_data.recipient_account},
        {"$inc": {"balance": transaction_data.amount}}
    )
    
    # Save transaction
    await db.transactions.insert_one(transaction.dict())
    
    return TransactionResponse(**transaction.dict())

@api_router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(current_user: User = Depends(get_current_user)):
    transactions = await db.transactions.find(
        {"$or": [{"sender_account": current_user.account_number}, {"recipient_account": current_user.account_number}]}
    ).sort("created_at", -1).to_list(100)
    
    return [TransactionResponse(**transaction) for transaction in transactions]

# Investment Routes
@api_router.post("/investments", response_model=InvestmentResponse)
async def create_investment(investment_data: InvestmentCreate, current_user: User = Depends(get_current_user)):
    # Check if user has sufficient balance
    if current_user.balance < investment_data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance"
        )
    
    # Calculate returns and maturity date
    expected_value, expected_return = calculate_investment_return(
        investment_data.amount, 
        investment_data.investment_type, 
        investment_data.duration_months
    )
    
    maturity_date = datetime.utcnow() + timedelta(days=investment_data.duration_months * 30)
    
    # Create investment
    investment = Investment(
        user_id=current_user.id,
        investment_type=investment_data.investment_type,
        amount=investment_data.amount,
        current_value=investment_data.amount,  # Initial value same as invested amount
        expected_return=expected_return,
        duration_months=investment_data.duration_months,
        maturity_date=maturity_date
    )
    
    # Deduct amount from user balance
    await db.users.update_one(
        {"id": current_user.id},
        {"$inc": {"balance": -investment_data.amount}}
    )
    
    # Save investment
    await db.investments.insert_one(investment.dict())
    
    # Create investment transaction
    transaction = Transaction(
        sender_account=current_user.account_number,
        recipient_account="INVESTMENT_POOL",
        amount=investment_data.amount,
        description=f"Investment in {investment_data.investment_type}",
        transaction_type=TransactionType.INVESTMENT,
        status=TransactionStatus.COMPLETED,
        completed_at=datetime.utcnow()
    )
    await db.transactions.insert_one(transaction.dict())
    
    return InvestmentResponse(**investment.dict())

@api_router.get("/investments", response_model=List[InvestmentResponse])
async def get_investments(current_user: User = Depends(get_current_user)):
    investments = await db.investments.find({"user_id": current_user.id}).to_list(100)
    return [InvestmentResponse(**investment) for investment in investments]

# Loan Routes
@api_router.post("/loans/apply", response_model=LoanResponse)
async def apply_loan(loan_data: LoanApplication, current_user: User = Depends(get_current_user)):
    # Calculate EMI
    interest_rates = {
        LoanType.PERSONAL: 10.5,
        LoanType.HOME: 8.5,
        LoanType.CAR: 9.5,
        LoanType.EDUCATION: 8.0,
        LoanType.BUSINESS: 11.0
    }
    
    interest_rate = interest_rates.get(loan_data.loan_type, 10.0)
    emi = calculate_emi(loan_data.amount, interest_rate, loan_data.duration_months)
    
    # Create loan application
    loan = Loan(
        user_id=current_user.id,
        loan_type=loan_data.loan_type,
        amount=loan_data.amount,
        purpose=loan_data.purpose,
        duration_months=loan_data.duration_months,
        monthly_income=loan_data.monthly_income,
        interest_rate=interest_rate,
        emi=emi
    )
    
    # Save loan application
    await db.loans.insert_one(loan.dict())
    
    return LoanResponse(**loan.dict())

@api_router.get("/loans", response_model=List[LoanResponse])
async def get_loans(current_user: User = Depends(get_current_user)):
    loans = await db.loans.find({"user_id": current_user.id}).to_list(100)
    return [LoanResponse(**loan) for loan in loans]

@api_router.put("/loans/{loan_id}/approve")
async def approve_loan(loan_id: str, current_user: User = Depends(get_current_user)):
    loan = await db.loans.find_one({"id": loan_id, "user_id": current_user.id})
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found"
        )
    
    # Update loan status
    await db.loans.update_one(
        {"id": loan_id},
        {"$set": {"status": LoanStatus.APPROVED, "approved_at": datetime.utcnow()}}
    )
    
    return {"message": "Loan approved successfully"}

# Chat Routes
@api_router.post("/chat", response_model=ChatMessageResponse)
async def send_chat_message(message_data: ChatMessageCreate, current_user: User = Depends(get_current_user)):
    # Generate response
    response = get_chat_response(message_data.message, message_data.category)
    
    # Create chat message
    chat_message = ChatMessage(
        user_id=current_user.id,
        message=message_data.message,
        response=response,
        category=message_data.category
    )
    
    # Save chat message
    await db.chat_messages.insert_one(chat_message.dict())
    
    return ChatMessageResponse(**chat_message.dict())

@api_router.get("/chat/history", response_model=List[ChatMessageResponse])
async def get_chat_history(current_user: User = Depends(get_current_user)):
    messages = await db.chat_messages.find({"user_id": current_user.id}).sort("created_at", -1).limit(50).to_list(50)
    return [ChatMessageResponse(**message) for message in messages]

# Health Check
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "bank": "Nexora Bank", "version": "1.0.0"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()