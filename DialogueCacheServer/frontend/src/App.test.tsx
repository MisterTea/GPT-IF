import { render, screen } from '@testing-library/react';
import App from './App';
import DataStore from './datastore';

const datastore = new DataStore();

test('renders learn react link', () => {
  render(<App datastore={datastore} />);
  const linkElement = screen.getByText(/learn react/i);
  expect(linkElement).toBeInTheDocument();
});
