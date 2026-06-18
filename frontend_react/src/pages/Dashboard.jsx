import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import Papa from 'papaparse';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Doughnut } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend);

export default function Dashboard() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const navigate = useNavigate();

  // Form State
  const [amount, setAmount] = useState('');
  const [type, setType] = useState('expense');
  const [desc, setDesc] = useState('');
  const [category, setCategory] = useState('');

  const fetchTransactions = async () => {
    try {
      const response = await api.get('/api/transactions');
      setTransactions(response.data);
    } catch (err) {
      console.error(err);
      if (err.response?.status === 401) {
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/api/transactions/${id}`);
      fetchTransactions(); // Refresh
    } catch (err) {
      alert("Failed to delete");
    }
  };

  const handleAddTransaction = async (e) => {
    e.preventDefault();
    
    // We must send the nested JSON structure expected by our Pydantic backend models!
    const txnData = {
      transaction_id: `TXN_${Date.now()}`,
      amount: parseFloat(amount),
      transaction_type: type,
      description: desc,
      timestamp: new Date().toISOString(),
      category: {
        category_id: Math.floor(Math.random() * 100),
        name: category || 'Misc',
        description: 'Added via web'
      },
      account: {
        account_id: 'ACC_1',
        account_type: 'Savings',
        balance: 0,
        currency: 'USD',
        user: {
          user_id: 'USR_WEB',
          full_name: 'Web User',
          email: 'web@test.com',
          is_active: true,
          created_at: new Date().toISOString()
        }
      }
    };

    try {
      await api.post('/api/transactions', txnData);
      setShowModal(false);
      fetchTransactions();
    } catch (err) {
      const errorMsg = err.response?.data?.errors 
        ? err.response.data.errors.join('\n')
        : err.response?.data?.detail || "Validation failed!";
      alert(`Backend Error:\n${errorMsg}`);
      console.error(err);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: async (results) => {
        const parsedRows = results.data;
        // Transform rows to match our Pydantic Schema
        const bulkTransactions = parsedRows.map((row, index) => {
          return {
            transaction_id: `TXN_CSV_${Date.now()}_${index}`,
            amount: parseFloat(row.Amount) || 0,
            transaction_type: (row.Type || 'expense').toLowerCase(),
            description: row.Description || 'Imported via CSV',
            timestamp: row.Date ? new Date(row.Date).toISOString() : new Date().toISOString(),
            category: {
              category_id: Math.floor(Math.random() * 100),
              name: row.Category || 'Misc',
              description: 'Imported Category'
            },
            account: {
              account_id: 'ACC_1',
              account_type: 'Savings',
              balance: 0,
              currency: 'USD',
              user: {
                user_id: 'USR_WEB',
                full_name: 'Web User',
                email: 'web@test.com',
                is_active: true,
                created_at: new Date().toISOString()
              }
            }
          };
        });

        // Filter out invalid rows (e.g. headers mistaken as rows or empty amounts <= 0)
        const validBulk = bulkTransactions.filter(t => t.amount > 0);

        if (validBulk.length === 0) {
          alert("No valid transactions found in CSV. Make sure headers match: Date, Description, Category, Amount, Type");
          return;
        }

        try {
          const res = await api.post('/api/transactions/bulk', validBulk);
          alert(res.data.message);
          fetchTransactions(); // Refresh dashboard instantly
        } catch (err) {
          console.error("Bulk upload failed", err);
          alert("Bulk import failed. See console for details.");
        }
      }
    });
  };

  // Calculations
  const income = transactions.filter(t => t.transaction_type === 'income').reduce((acc, t) => acc + t.amount, 0);
  const expense = transactions.filter(t => t.transaction_type === 'expense').reduce((acc, t) => acc + t.amount, 0);
  const balance = income - expense;

  // Chart Data
  const chartData = {
    labels: ['Income', 'Expense'],
    datasets: [{
      data: [income, expense],
      backgroundColor: ['#10b981', '#ef4444'],
      borderWidth: 0,
      hoverOffset: 4
    }]
  };

  if (loading) return <div style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: '20vh' }}>Loading...</div>;

  return (
    <div className="container animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h2>Expense Dashboard</h2>
        <button className="btn btn-outline" onClick={handleLogout}>Logout</button>
      </div>

      {/* Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <div className="glass-card">
          <p style={{ color: 'var(--text-muted)' }}>Total Balance</p>
          <h3 style={{ fontSize: '2rem', color: balance >= 0 ? 'var(--accent)' : 'var(--danger)' }}>
            ${balance.toFixed(2)}
          </h3>
        </div>
        <div className="glass-card">
          <p style={{ color: 'var(--text-muted)' }}>Income</p>
          <h3 style={{ fontSize: '2rem', color: 'var(--accent)' }}>+${income.toFixed(2)}</h3>
        </div>
        <div className="glass-card">
          <p style={{ color: 'var(--text-muted)' }}>Expenses</p>
          <h3 style={{ fontSize: '2rem', color: 'var(--danger)' }}>-${expense.toFixed(2)}</h3>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '2rem' }}>
        {/* Transaction Table */}
        <div className="glass-card" style={{ overflowX: 'auto' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '1rem' }}>
            <h3>Recent Transactions</h3>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <label className="btn btn-outline" style={{ cursor: 'pointer' }}>
                Import CSV
                <input 
                  type="file" 
                  accept=".csv" 
                  style={{ display: 'none' }} 
                  onChange={handleFileUpload} 
                />
              </label>
              <button className="btn btn-primary" onClick={() => setShowModal(true)}>+ Add</button>
            </div>
          </div>
          
          <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ padding: '1rem 0' }}>Date</th>
                <th>Description</th>
                <th>Category</th>
                <th>Amount</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map(txn => (
                <tr key={txn.transaction_id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '1rem 0' }}>{new Date(txn.timestamp).toLocaleDateString()}</td>
                  <td>{txn.description}</td>
                  <td>{txn.category_id}</td>
                  <td style={{ color: txn.transaction_type === 'income' ? 'var(--accent)' : 'var(--danger)', fontWeight: 'bold' }}>
                    {txn.transaction_type === 'income' ? '+' : '-'}${txn.amount}
                  </td>
                  <td>
                    <button className="btn btn-danger" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }} onClick={() => handleDelete(txn.transaction_id)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
              {transactions.length === 0 && (
                <tr><td colSpan="5" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>No transactions found.</td></tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Chart */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <h3 style={{ marginBottom: '1rem' }}>Overview</h3>
          {income === 0 && expense === 0 ? (
            <p style={{ color: 'var(--text-muted)', marginTop: '2rem' }}>Add data to see chart</p>
          ) : (
             <div style={{ width: '200px' }}><Doughnut data={chartData} options={{ cutout: '75%' }} /></div>
          )}
        </div>
      </div>

      {/* Add Modal */}
      {showModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(5px)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 100 }}>
          <div className="glass-card animate-fade-in" style={{ width: '400px' }}>
            <h3 style={{ marginBottom: '1.5rem' }}>Add Transaction</h3>
            <form onSubmit={handleAddTransaction}>
              <div className="input-group">
                <label>Type</label>
                <select className="input-field" value={type} onChange={e => setType(e.target.value)}>
                  <option value="expense">Expense</option>
                  <option value="income">Income</option>
                </select>
              </div>
              <div className="input-group">
                <label>Amount</label>
                <input type="number" step="0.01" className="input-field" required value={amount} onChange={e => setAmount(e.target.value)} />
              </div>
              <div className="input-group">
                <label>Description</label>
                <input type="text" className="input-field" required value={desc} onChange={e => setDesc(e.target.value)} />
              </div>
              <div className="input-group">
                <label>Category Name</label>
                <input type="text" className="input-field" required value={category} onChange={e => setCategory(e.target.value)} />
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>Save</button>
                <button type="button" className="btn btn-outline" style={{ flex: 1 }} onClick={() => setShowModal(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
