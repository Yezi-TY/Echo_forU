/**
 * LyricsEditor 组件测试
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import { LyricsEditor } from '../../components/LyricsEditor';

describe('LyricsEditor', () => {
  it('renders correctly', () => {
    const handleChange = jest.fn();
    render(<LyricsEditor value="" onChange={handleChange} />);
    
    expect(screen.getByPlaceholderText(/lyrics/i)).toBeInTheDocument();
  });

  it('calls onChange when text changes', () => {
    const handleChange = jest.fn();
    render(<LyricsEditor value="" onChange={handleChange} />);
    
    const input = screen.getByPlaceholderText(/lyrics/i);
    // 这里可以添加更多测试
  });
});

