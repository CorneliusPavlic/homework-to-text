import { render, screen } from '@testing-library/react';
import Scanner from './Scanner';

test('renders learn react link', () => {
  render(<Scanner />);
  const linkElement = screen.getByText(/learn react/i);
  expect(linkElement).toBeInTheDocument();
});
