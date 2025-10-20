import '../styles/globals.css';
import QueryProvider from '../providers/QueryProvider';

export default function RootLayout({ children }:{ children: React.ReactNode }) {
  return (
    <html lang="en"><body>
      <div className="container">
        <h1>File Upload Demo</h1>
          <QueryProvider>{children}</QueryProvider>
      </div>
    </body></html>
  );
}
