'use client'; // חייב להיות Client Component

import { useState, useEffect } from 'react';
import { useDebounce } from 'use-debounce';

export function FoodSearch() {
  const [text, setText] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // השהיה של 300 מילישניות כדי לא להציף את השרת
  const [query] = useDebounce(text, 300);

  useEffect(() => {
    const fetchData = async () => {
      if (!query) {
        setResults([]);
        return;
      }

      setLoading(true);
      try {
        const params = new URLSearchParams({
          location: "/api/ingredients/",
          info: query,
        });
        
        const response = await fetch(`localhost{params}`);
        const data = await response.json();
        
        if (data.success) {
          setResults(data.res); // הנתונים מה-Serializer ב-Django
        }
      } catch (error) {
        console.error("Error fetching food:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [query]);

  return (
    <div className="max-w-md mx-auto p-4">
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter food"
        className="w-full p-3 border rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 outline-none text-black"
      />

      {loading && <p className="mt-2 text-gray-500">Searching...</p>}

      <ul className="mt-4 space-y-2">
        {results.map((item: any) => (
          <li key={item.id} className="p-3 border-b hover:bg-gray-50 transition-colors cursor-pointer">
            <div className="font-bold">{item.name}</div>
            <div className="text-sm text-gray-500">
               {item.description} • <span className="text-blue-600">{item.fat_str}</span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}