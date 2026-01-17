'use client'; // חייב להיות Client Component

import { useState, useEffect, useRef } from 'react';
import { useDebounce } from 'use-debounce';
import { ingredientsAPI } from '@/lib/api';

interface Ingredient {
  id: number;
  name: string;
  category?: string;
  description?: string;
  fat_str?: string;
}

interface FoodSearchProps {
  value?: string;
  onChange?: (value: string) => void;
  onSelect?: (ingredient: Ingredient) => void;
  onValidSelection?: (isValid: boolean) => void;
  placeholder?: string;
  className?: string;
}

export function FoodSearch({ value = '', onChange, onSelect, onValidSelection, placeholder = "Enter ingredient name", className = "" }: FoodSearchProps) {
  const [text, setText] = useState(value);
  const [results, setResults] = useState<Ingredient[]>([]);
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [selectedIngredient, setSelectedIngredient] = useState<Ingredient | null>(null);
  const [isValidSelection, setIsValidSelection] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  
  // השהיה של 300 מילישניות כדי לא להציף את השרת
  const [query] = useDebounce(text, 300);

  useEffect(() => {
    if (value && selectedIngredient && value === selectedIngredient.name) {
      setText(value);
    } else if (!value) {
      setText('');
      setSelectedIngredient(null);
      setIsValidSelection(false);
    }
  }, [value, selectedIngredient]);

  useEffect(() => {
    const fetchData = async () => {
      if (!query || query.trim().length === 0) {
        setResults([]);
        setShowResults(false);
        return;
      }

      setLoading(true);
      try {
        const results = await ingredientsAPI.searchIngredients(query);
        setResults(results || []);
        setShowResults(true);
      } catch (error) {
        console.error("Error fetching food:", error);
        setResults([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [query]);

  // Close results when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setShowResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleSelect = (item: Ingredient) => {
    setText(item.name);
    setSelectedIngredient(item);
    setIsValidSelection(true);
    setShowResults(false);
    if (onChange) {
      onChange(item.name);
    }
    if (onSelect) {
      onSelect(item);
    }
    if (onValidSelection) {
      onValidSelection(true);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setText(newValue);
    // Clear selection if user types something different
    if (selectedIngredient && newValue !== selectedIngredient.name) {
      setSelectedIngredient(null);
      setIsValidSelection(false);
      if (onValidSelection) {
        onValidSelection(false);
      }
    }
    setShowResults(true);
    if (onChange) {
      onChange(newValue);
    }
  };

  const handleBlur = () => {
    // Clear input if it's not a valid selection
    if (!isValidSelection && text) {
      setText('');
      if (onChange) {
        onChange('');
      }
      setSelectedIngredient(null);
    }
    // Delay hiding results to allow click events
    setTimeout(() => setShowResults(false), 200);
  };

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      <input
        type="text"
        value={text}
        onChange={handleInputChange}
        onFocus={() => {
          if (results.length > 0) {
            setShowResults(true);
          }
        }}
        onBlur={handleBlur}
        placeholder={placeholder}
        className={`w-full px-3 py-2 border rounded text-black focus:outline-none focus:ring-2 ${
          isValidSelection 
            ? 'border-black focus:ring-black' 
            : 'border-red-500 focus:ring-red-500'
        }`}
      />
      {text && !isValidSelection && (
        <p className="text-xs text-red-500 mt-1">Please select an option from the list</p>
      )}

      {loading && (
        <div className="absolute z-[10001] w-full mt-1 bg-white border border-black rounded shadow-lg p-2">
          <p className="text-sm text-gray-500">Searching...</p>
        </div>
      )}

      {showResults && results.length > 0 && !loading && (
        <ul className="absolute z-[10001] w-full mt-1 bg-white border border-black rounded shadow-lg max-h-60 overflow-y-auto">
          {results.map((item: Ingredient) => (
            <li
              key={item.id}
              onMouseDown={(e) => {
                e.preventDefault(); // Prevent input blur
                handleSelect(item);
              }}
              className="p-3 border-b border-gray-200 hover:bg-gray-100 transition-colors cursor-pointer last:border-b-0"
            >
              <div className="font-medium text-black">{item.name}</div>
              {item.description && (
                <div className="text-sm text-gray-600">
                  {item.description} {item.fat_str && `• ${item.fat_str}`}
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}