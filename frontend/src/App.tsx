import { useState, useEffect } from "react";
import { io } from "socket.io-client";

const socket = io("http://localhost:5000");

export default function WalletApp() {
  const [userId, setUserId] = useState("");
  const [loggedIn, setLoggedIn] = useState(false);
  const [balance, setBalance] = useState<number | null>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [receiverId, setReceiverId] = useState("");
  const [amount, setAmount] = useState("");
  const [message, setMessage] = useState("");

  // Fetch balance + history API
  const fetchUserData = async (id: string) => {
    try {
      const res = await fetch(`http://localhost:5000/history/${id}`);
      const tx = await res.json();

      const balRes = await fetch(`http://localhost:5000/balance/${id}`);
      const bal = await balRes.json();

      setHistory(tx);
      setBalance(bal.balance);
    } catch (err) {
      console.error(err);
    }
  };

  // Login
  const handleLogin = () => {
    setLoggedIn(true);
    fetchUserData(userId);
  };

  // Transfer money
  const handleSend = async () => {
    try {
      const res = await fetch("http://localhost:5000/transfer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sender_id: Number(userId),
          receiver_id: Number(receiverId),
          amount: Number(amount),
        }),
      });
      const data = await res.json();
      setMessage(data.message || data.error);
    } catch (err) {
      console.error(err);
    }
  };

  // Socket listeners
  useEffect(() => {
    socket.on("balance_update", (data: any) => {
      if (String(data.user_id) === String(userId)) {
        setBalance(data.balance);
      }
    });

    socket.on("new_transaction", (tx: any) => {
      if (String(tx.sender_id) === String(userId) || String(tx.receiver_id) === String(userId)) {
        setHistory(prev => [tx, ...prev]);
      }
    });
  }, [userId]);

  return (
    <div className="min-h-screen bg-gray-100 p-8 flex flex-col items-center gap-6">
      {!loggedIn && (
        <div className="bg-white p-6 rounded-2xl shadow-xl w-full max-w-md flex flex-col gap-4 border border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900">Login</h1>
          <input
            placeholder="Enter User ID"
            className="p-3 border rounded-lg bg-gray-50"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
          />
          <button
            className="p-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700"
            onClick={handleLogin}
          >
            Login
          </button>
        </div>
      )}

      {loggedIn && (
        <div className="w-full max-w-4xl flex flex-col gap-8">
          {/* Balance Card */}
          <div className="bg-white shadow-xl p-6 rounded-2xl border border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">Your Balance</h2>
            <div className="text-4xl font-semibold text-green-600 mt-2">
              {balance !== null ? `${balance} ₹` : "Loading..."}
            </div>
          </div>

          {/* Transfer UI */}
          <div className="bg-white shadow-xl p-6 rounded-2xl border border-gray-200 flex flex-col gap-4">
            <h2 className="text-xl font-bold">Send Money</h2>
            <input
              placeholder="Receiver ID"
              className="p-3 border rounded-lg bg-gray-50"
              value={receiverId}
              onChange={(e) => setReceiverId(e.target.value)}
            />
            <input
              placeholder="Amount"
              className="p-3 border rounded-lg bg-gray-50"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />
            <button
              className="p-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700"
              onClick={handleSend}
            >
              Send
            </button>
            {message && <p className="text-gray-700 font-medium">{message}</p>}
          </div>

          {/* History Table */}
          <div className="bg-white shadow-xl p-6 rounded-2xl border border-gray-200">
            <h2 className="text-xl font-bold mb-4">Transaction History</h2>
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-200 text-gray-800">
                  <th className="p-3">TX_ID</th>
                  <th className="p-3">Created_At</th>
                  <th className="p-3">Sender</th>
                  <th className="p-3">Receiver</th>
                  <th className="p-3">Amount</th>
                </tr>
              </thead>
              <tbody>
                {history.map((tx, i) => (
                  <tr key={i} className="border-b hover:bg-gray-50">
                    <td className="p-3">{tx.transaction_id}</td>
                    <td className="p-3">{tx.created_at}</td>
                    <td className="p-3">{tx.sender_id}</td>
                    <td className="p-3">{tx.receiver_id}</td>
                    <td className="p-3 font-semibold text-blue-700">{tx.amount}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
