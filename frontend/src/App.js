import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Token management
const getToken = () => localStorage.getItem('token');
const setToken = (token) => localStorage.setItem('token', token);
const removeToken = () => localStorage.removeItem('token');

// Axios interceptor for authentication
axios.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Chat Component
const ChatBox = ({ user }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [category, setCategory] = useState('general');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      fetchChatHistory();
    }
  }, [isOpen]);

  const fetchChatHistory = async () => {
    try {
      const response = await axios.get(`${API}/chat/history`);
      setMessages(response.data.reverse());
    } catch (error) {
      console.error('Failed to fetch chat history:', error);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post(`${API}/chat`, {
        message: newMessage,
        category: category
      });

      setMessages([...messages, response.data]);
      setNewMessage('');
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Chat Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="bg-blue-600 hover:bg-blue-700 text-white rounded-full p-4 shadow-lg transition duration-200"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="absolute bottom-16 right-0 w-96 h-96 bg-white rounded-lg shadow-xl border border-gray-200">
          {/* Chat Header */}
          <div className="bg-blue-600 text-white p-4 rounded-t-lg">
            <h3 className="font-semibold">Nexora Bank Assistant</h3>
            <p className="text-sm opacity-90">How can I help you today?</p>
          </div>

          {/* Category Selection */}
          <div className="p-3 border-b border-gray-200">
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500"
            >
              <option value="general">General Inquiry</option>
              <option value="loan">Loan Information</option>
              <option value="investment">Investment Advice</option>
            </select>
          </div>

          {/* Messages */}
          <div className="flex-1 p-4 h-48 overflow-y-auto">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 text-sm">
                Start a conversation! Ask about loans, investments, or general banking.
              </div>
            )}
            {messages.map((msg, index) => (
              <div key={index} className="mb-4">
                <div className="bg-blue-100 p-2 rounded-lg mb-2">
                  <p className="text-sm text-gray-800">{msg.message}</p>
                </div>
                <div className="bg-gray-100 p-2 rounded-lg">
                  <p className="text-sm text-gray-700">{msg.response}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Message Input */}
          <div className="p-3 border-t border-gray-200">
            <div className="flex space-x-2">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
                disabled={loading}
              />
              <button
                onClick={sendMessage}
                disabled={loading || !newMessage.trim()}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm disabled:opacity-50"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Money Transfer Component
const MoneyTransfer = ({ user, onBack }) => {
  const [formData, setFormData] = useState({
    recipient_account: '',
    amount: '',
    description: ''
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await axios.post(`${API}/transactions/transfer`, {
        recipient_account: formData.recipient_account,
        amount: parseFloat(formData.amount),
        description: formData.description
      });

      setSuccess('Transfer completed successfully!');
      setFormData({ recipient_account: '', amount: '', description: '' });
    } catch (error) {
      setError(error.response?.data?.detail || 'Transfer failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-xl shadow-sm p-8">
        <div className="flex items-center mb-6">
          <button
            onClick={onBack}
            className="mr-4 text-blue-600 hover:text-blue-800"
          >
            ← Back
          </button>
          <h2 className="text-2xl font-bold text-gray-800">Transfer Money</h2>
        </div>

        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-4">
            {success}
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Recipient Account Number
            </label>
            <input
              type="text"
              name="recipient_account"
              value={formData.recipient_account}
              onChange={handleInputChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Enter recipient account number"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Amount (₹)
            </label>
            <input
              type="number"
              name="amount"
              value={formData.amount}
              onChange={handleInputChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Enter amount"
              min="1"
              max={user.balance}
              required
            />
            <p className="text-sm text-gray-500 mt-1">Available balance: ₹{user.balance?.toLocaleString()}</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description (Optional)
            </label>
            <input
              type="text"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Enter transfer description"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition duration-200 disabled:opacity-50"
          >
            {loading ? 'Processing...' : 'Transfer Money'}
          </button>
        </form>
      </div>
    </div>
  );
};

// Transaction History Component
const TransactionHistory = ({ onBack }) => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTransactions();
  }, []);

  const fetchTransactions = async () => {
    try {
      const response = await axios.get(`${API}/transactions`);
      setTransactions(response.data);
    } catch (error) {
      console.error('Failed to fetch transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTransactionIcon = (type) => {
    switch (type) {
      case 'transfer':
        return '💸';
      case 'investment':
        return '📈';
      case 'deposit':
        return '💰';
      case 'withdrawal':
        return '🏧';
      default:
        return '💳';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-xl shadow-sm p-8">
        <div className="flex items-center mb-6">
          <button
            onClick={onBack}
            className="mr-4 text-blue-600 hover:text-blue-800"
          >
            ← Back
          </button>
          <h2 className="text-2xl font-bold text-gray-800">Transaction History</h2>
        </div>

        {transactions.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No transactions found</p>
          </div>
        ) : (
          <div className="space-y-4">
            {transactions.map((transaction) => (
              <div key={transaction.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <span className="text-2xl mr-3">{getTransactionIcon(transaction.transaction_type)}</span>
                    <div>
                      <p className="font-semibold text-gray-800">
                        {transaction.description || `${transaction.transaction_type} Transaction`}
                      </p>
                      <p className="text-sm text-gray-600">
                        {transaction.sender_account} → {transaction.recipient_account}
                      </p>
                      <p className="text-sm text-gray-500">
                        {new Date(transaction.created_at).toLocaleDateString()} at {new Date(transaction.created_at).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-semibold text-gray-800">₹{transaction.amount.toLocaleString()}</p>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      transaction.status === 'completed' ? 'bg-green-100 text-green-800' : 
                      transaction.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 
                      'bg-red-100 text-red-800'
                    }`}>
                      {transaction.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Investment Component
const Investments = ({ onBack }) => {
  const [investments, setInvestments] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    investment_type: 'mutual_fund',
    amount: '',
    duration_months: 12
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchInvestments();
  }, []);

  const fetchInvestments = async () => {
    try {
      const response = await axios.get(`${API}/investments`);
      setInvestments(response.data);
    } catch (error) {
      console.error('Failed to fetch investments:', error);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await axios.post(`${API}/investments`, {
        investment_type: formData.investment_type,
        amount: parseFloat(formData.amount),
        duration_months: parseInt(formData.duration_months)
      });

      setSuccess('Investment created successfully!');
      setFormData({ investment_type: 'mutual_fund', amount: '', duration_months: 12 });
      setShowForm(false);
      fetchInvestments();
    } catch (error) {
      setError(error.response?.data?.detail || 'Investment failed');
    } finally {
      setLoading(false);
    }
  };

  const investmentOptions = {
    mutual_fund: { name: 'Mutual Fund', icon: '📈', returns: '12%' },
    fixed_deposit: { name: 'Fixed Deposit', icon: '🏦', returns: '6.5%' },
    equity: { name: 'Equity', icon: '📊', returns: '15%' },
    bonds: { name: 'Government Bonds', icon: '💎', returns: '7.5%' },
    gold: { name: 'Digital Gold', icon: '🥇', returns: '8%' }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white rounded-xl shadow-sm p-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center">
            <button
              onClick={onBack}
              className="mr-4 text-blue-600 hover:text-blue-800"
            >
              ← Back
            </button>
            <h2 className="text-2xl font-bold text-gray-800">Investments</h2>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            {showForm ? 'Cancel' : 'New Investment'}
          </button>
        </div>

        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-4">
            {success}
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        {/* Investment Form */}
        {showForm && (
          <div className="bg-gray-50 rounded-lg p-6 mb-6">
            <h3 className="text-lg font-semibold mb-4">Create New Investment</h3>
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Investment Type
                </label>
                <select
                  name="investment_type"
                  value={formData.investment_type}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  {Object.entries(investmentOptions).map(([key, option]) => (
                    <option key={key} value={key}>
                      {option.icon} {option.name} ({option.returns})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Amount (₹)
                </label>
                <input
                  type="number"
                  name="amount"
                  value={formData.amount}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter amount"
                  min="1000"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Duration (Months)
                </label>
                <select
                  name="duration_months"
                  value={formData.duration_months}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value={6}>6 Months</option>
                  <option value={12}>1 Year</option>
                  <option value={24}>2 Years</option>
                  <option value={36}>3 Years</option>
                  <option value={60}>5 Years</option>
                </select>
              </div>

              <div className="md:col-span-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg disabled:opacity-50"
                >
                  {loading ? 'Creating...' : 'Create Investment'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Investments List */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {investments.map((investment) => {
            const option = investmentOptions[investment.investment_type];
            return (
              <div key={investment.id} className="border border-gray-200 rounded-lg p-6">
                <div className="flex items-center mb-4">
                  <span className="text-2xl mr-3">{option.icon}</span>
                  <div>
                    <h3 className="font-semibold text-gray-800">{option.name}</h3>
                    <p className="text-sm text-gray-600">Expected Returns: {option.returns}</p>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Invested:</span>
                    <span className="font-semibold">₹{investment.amount.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Current Value:</span>
                    <span className="font-semibold text-green-600">₹{investment.current_value.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Expected Return:</span>
                    <span className="font-semibold text-blue-600">₹{investment.expected_return.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Maturity:</span>
                    <span className="text-sm">{new Date(investment.maturity_date).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {investments.length === 0 && !showForm && (
          <div className="text-center py-12">
            <p className="text-gray-500">No investments found. Start investing today!</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Loans Component
const Loans = ({ onBack }) => {
  const [loans, setLoans] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    loan_type: 'personal',
    amount: '',
    purpose: '',
    duration_months: 12,
    monthly_income: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchLoans();
  }, []);

  const fetchLoans = async () => {
    try {
      const response = await axios.get(`${API}/loans`);
      setLoans(response.data);
    } catch (error) {
      console.error('Failed to fetch loans:', error);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await axios.post(`${API}/loans/apply`, {
        loan_type: formData.loan_type,
        amount: parseFloat(formData.amount),
        purpose: formData.purpose,
        duration_months: parseInt(formData.duration_months),
        monthly_income: parseFloat(formData.monthly_income)
      });

      setSuccess('Loan application submitted successfully!');
      setFormData({
        loan_type: 'personal',
        amount: '',
        purpose: '',
        duration_months: 12,
        monthly_income: ''
      });
      setShowForm(false);
      fetchLoans();
    } catch (error) {
      setError(error.response?.data?.detail || 'Loan application failed');
    } finally {
      setLoading(false);
    }
  };

  const loanTypes = {
    personal: { name: 'Personal Loan', icon: '💳', rate: '10.5%' },
    home: { name: 'Home Loan', icon: '🏠', rate: '8.5%' },
    car: { name: 'Car Loan', icon: '🚗', rate: '9.5%' },
    education: { name: 'Education Loan', icon: '🎓', rate: '8.0%' },
    business: { name: 'Business Loan', icon: '🏢', rate: '11.0%' }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white rounded-xl shadow-sm p-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center">
            <button
              onClick={onBack}
              className="mr-4 text-blue-600 hover:text-blue-800"
            >
              ← Back
            </button>
            <h2 className="text-2xl font-bold text-gray-800">Loans</h2>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            {showForm ? 'Cancel' : 'Apply for Loan'}
          </button>
        </div>

        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-4">
            {success}
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        {/* Loan Application Form */}
        {showForm && (
          <div className="bg-gray-50 rounded-lg p-6 mb-6">
            <h3 className="text-lg font-semibold mb-4">Apply for Loan</h3>
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Loan Type
                </label>
                <select
                  name="loan_type"
                  value={formData.loan_type}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  {Object.entries(loanTypes).map(([key, type]) => (
                    <option key={key} value={key}>
                      {type.icon} {type.name} ({type.rate})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Loan Amount (₹)
                </label>
                <input
                  type="number"
                  name="amount"
                  value={formData.amount}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter loan amount"
                  min="10000"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Monthly Income (₹)
                </label>
                <input
                  type="number"
                  name="monthly_income"
                  value={formData.monthly_income}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter monthly income"
                  min="10000"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Duration (Months)
                </label>
                <select
                  name="duration_months"
                  value={formData.duration_months}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value={12}>1 Year</option>
                  <option value={24}>2 Years</option>
                  <option value={36}>3 Years</option>
                  <option value={60}>5 Years</option>
                  <option value={120}>10 Years</option>
                  <option value={240}>20 Years</option>
                  <option value={360}>30 Years</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Purpose
                </label>
                <input
                  type="text"
                  name="purpose"
                  value={formData.purpose}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter purpose of loan"
                  required
                />
              </div>

              <div className="md:col-span-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg disabled:opacity-50"
                >
                  {loading ? 'Submitting...' : 'Apply for Loan'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Loans List */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loans.map((loan) => {
            const type = loanTypes[loan.loan_type];
            return (
              <div key={loan.id} className="border border-gray-200 rounded-lg p-6">
                <div className="flex items-center mb-4">
                  <span className="text-2xl mr-3">{type.icon}</span>
                  <div>
                    <h3 className="font-semibold text-gray-800">{type.name}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      loan.status === 'approved' ? 'bg-green-100 text-green-800' : 
                      loan.status === 'applied' ? 'bg-yellow-100 text-yellow-800' : 
                      'bg-red-100 text-red-800'
                    }`}>
                      {loan.status}
                    </span>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Amount:</span>
                    <span className="font-semibold">₹{loan.amount.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Interest Rate:</span>
                    <span className="font-semibold">{loan.interest_rate}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">EMI:</span>
                    <span className="font-semibold text-blue-600">₹{loan.emi.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Duration:</span>
                    <span className="text-sm">{loan.duration_months} months</span>
                  </div>
                  <div className="pt-2">
                    <p className="text-sm text-gray-600">
                      <strong>Purpose:</strong> {loan.purpose}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {loans.length === 0 && !showForm && (
          <div className="text-center py-12">
            <p className="text-gray-500">No loan applications found. Apply for a loan today!</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Login Component
const LoginPage = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    phone: '',
    account_type: 'savings'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/register';
      const payload = isLogin 
        ? { email: formData.email, password: formData.password }
        : formData;

      const response = await axios.post(`${API}${endpoint}`, payload);
      
      if (response.data.access_token) {
        setToken(response.data.access_token);
        onLogin(response.data.user);
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-blue-100">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center">
            <div className="text-2xl font-bold text-blue-800">Nexora</div>
            <div className="ml-2 text-sm text-blue-600">Bank</div>
          </div>
        </div>
      </div>

      <div className="flex min-h-screen">
        {/* Left Side - Hero Image */}
        <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-600 to-blue-800 items-center justify-center p-12">
          <div className="max-w-md text-white text-center">
            <img 
              src="https://images.unsplash.com/photo-1586108562388-f392017e9cda?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzB8MHwxfHNlYXJjaHwzfHxiYW5raW5nfGVufDB8fHxibHVlfDE3NTM1MjQ4NDF8MA&ixlib=rb-4.1.0&q=85"
              alt="Nexora Bank"
              className="w-full h-64 object-cover rounded-lg mb-8 shadow-lg"
            />
            <h1 className="text-4xl font-bold mb-4">Welcome to Nexora Bank</h1>
            <p className="text-xl text-blue-100">
              Secure, Modern, and Trusted Banking Solutions
            </p>
            <div className="mt-8 grid grid-cols-2 gap-4 text-sm">
              <div className="bg-white/10 p-4 rounded-lg">
                <div className="text-2xl font-bold">24/7</div>
                <div>Online Banking</div>
              </div>
              <div className="bg-white/10 p-4 rounded-lg">
                <div className="text-2xl font-bold">100%</div>
                <div>Secure</div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Login Form */}
        <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
          <div className="max-w-md w-full">
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-800">
                  {isLogin ? 'Sign In' : 'Create Account'}
                </h2>
                <p className="text-gray-600 mt-2">
                  {isLogin ? 'Access your account securely' : 'Join Nexora Bank today'}
                </p>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-6">
                {!isLogin && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Full Name
                      </label>
                      <input
                        type="text"
                        name="full_name"
                        value={formData.full_name}
                        onChange={handleInputChange}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
                        placeholder="Enter your full name"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Phone Number
                      </label>
                      <input
                        type="tel"
                        name="phone"
                        value={formData.phone}
                        onChange={handleInputChange}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
                        placeholder="Enter your phone number"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Account Type
                      </label>
                      <select
                        name="account_type"
                        value={formData.account_type}
                        onChange={handleInputChange}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
                      >
                        <option value="savings">Savings Account</option>
                        <option value="current">Current Account</option>
                        <option value="salary">Salary Account</option>
                      </select>
                    </div>
                  </>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
                    placeholder="Enter your email"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Password
                  </label>
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
                    placeholder="Enter your password"
                    required
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Create Account')}
                </button>
              </form>

              <div className="text-center mt-6">
                <button
                  onClick={() => setIsLogin(!isLogin)}
                  className="text-blue-600 hover:text-blue-800 font-medium"
                >
                  {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Dashboard Component
const Dashboard = ({ user, onLogout }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState('dashboard');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/summary`);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post(`${API}/auth/logout`);
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      removeToken();
      onLogout();
    }
  };

  const navigateTo = (page) => {
    setCurrentPage(page);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  // Render different pages based on currentPage state
  if (currentPage === 'transfer') {
    return (
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center">
                <div className="text-2xl font-bold text-blue-800">Nexora</div>
                <div className="ml-2 text-sm text-blue-600">Bank</div>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-gray-700">Welcome, {user.full_name}</span>
                <button
                  onClick={handleLogout}
                  className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition duration-200"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </nav>
        <div className="max-w-7xl mx-auto px-4 py-8">
          <MoneyTransfer user={user} onBack={() => navigateTo('dashboard')} />
        </div>
        <ChatBox user={user} />
      </div>
    );
  }

  if (currentPage === 'transactions') {
    return (
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center">
                <div className="text-2xl font-bold text-blue-800">Nexora</div>
                <div className="ml-2 text-sm text-blue-600">Bank</div>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-gray-700">Welcome, {user.full_name}</span>
                <button
                  onClick={handleLogout}
                  className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition duration-200"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </nav>
        <div className="max-w-7xl mx-auto px-4 py-8">
          <TransactionHistory onBack={() => navigateTo('dashboard')} />
        </div>
        <ChatBox user={user} />
      </div>
    );
  }

  if (currentPage === 'investments') {
    return (
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center">
                <div className="text-2xl font-bold text-blue-800">Nexora</div>
                <div className="ml-2 text-sm text-blue-600">Bank</div>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-gray-700">Welcome, {user.full_name}</span>
                <button
                  onClick={handleLogout}
                  className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition duration-200"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </nav>
        <div className="max-w-7xl mx-auto px-4 py-8">
          <Investments onBack={() => navigateTo('dashboard')} />
        </div>
        <ChatBox user={user} />
      </div>
    );
  }

  if (currentPage === 'loans') {
    return (
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center">
                <div className="text-2xl font-bold text-blue-800">Nexora</div>
                <div className="ml-2 text-sm text-blue-600">Bank</div>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-gray-700">Welcome, {user.full_name}</span>
                <button
                  onClick={handleLogout}
                  className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition duration-200"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </nav>
        <div className="max-w-7xl mx-auto px-4 py-8">
          <Loans onBack={() => navigateTo('dashboard')} />
        </div>
        <ChatBox user={user} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <div className="text-2xl font-bold text-blue-800">Nexora</div>
              <div className="ml-2 text-sm text-blue-600">Bank</div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Welcome, {user.full_name}</span>
              <button
                onClick={handleLogout}
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition duration-200"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Account Summary */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-2xl text-white p-8 mb-8">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold mb-2">Account Dashboard</h1>
              <p className="text-blue-100">Account Number: {dashboardData?.account_number}</p>
            </div>
            <div className="text-right">
              <p className="text-blue-100 text-sm">Available Balance</p>
              <p className="text-4xl font-bold">₹{user.balance?.toLocaleString()}</p>
            </div>
          </div>
          <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white/10 p-4 rounded-lg">
              <p className="text-blue-100 text-sm">Account Type</p>
              <p className="font-semibold capitalize">{dashboardData?.account_type}</p>
            </div>
            <div className="bg-white/10 p-4 rounded-lg">
              <p className="text-blue-100 text-sm">Total Investments</p>
              <p className="font-semibold">₹{dashboardData?.total_investments?.toLocaleString() || '0'}</p>
            </div>
            <div className="bg-white/10 p-4 rounded-lg">
              <p className="text-blue-100 text-sm">Active Loans</p>
              <p className="font-semibold">₹{dashboardData?.total_loans?.toLocaleString() || '0'}</p>
            </div>
            <div className="bg-white/10 p-4 rounded-lg">
              <p className="text-blue-100 text-sm">Transactions</p>
              <p className="font-semibold">{dashboardData?.recent_transactions_count || 0}</p>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div 
            onClick={() => navigateTo('transfer')}
            className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition duration-200 cursor-pointer"
          >
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-800 mb-2">Transfer Money</h3>
            <p className="text-gray-600 text-sm">Send money securely</p>
          </div>

          <div 
            onClick={() => navigateTo('transactions')}
            className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition duration-200 cursor-pointer"
          >
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-800 mb-2">Transaction History</h3>
            <p className="text-gray-600 text-sm">View your transactions</p>
          </div>

          <div 
            onClick={() => navigateTo('investments')}
            className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition duration-200 cursor-pointer"
          >
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-800 mb-2">Investments</h3>
            <p className="text-gray-600 text-sm">Grow your wealth</p>
          </div>

          <div 
            onClick={() => navigateTo('loans')}
            className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition duration-200 cursor-pointer"
          >
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-800 mb-2">Loans</h3>
            <p className="text-gray-600 text-sm">Apply for loans</p>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Recent Activity</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                  <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="font-medium text-gray-800">Account Created</p>
                  <p className="text-gray-600 text-sm">Welcome to Nexora Bank!</p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-semibold text-green-600">₹10,000</p>
                <p className="text-gray-500 text-sm">Today</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Box */}
      <ChatBox user={user} />
    </div>
  );
};

// Main App Component
function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    const token = getToken();
    if (token) {
      try {
        const response = await axios.get(`${API}/auth/me`);
        setUser(response.data);
      } catch (error) {
        console.error('Auth check failed:', error);
        removeToken();
      }
    }
    setLoading(false);
  };

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading Nexora Bank...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      {user ? (
        <Dashboard user={user} onLogout={handleLogout} />
      ) : (
        <LoginPage onLogin={handleLogin} />
      )}
    </div>
  );
}

export default App;