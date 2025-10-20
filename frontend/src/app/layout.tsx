import '../styles/globals.css';
export default function RootLayout({ children }:{ children: React.ReactNode }) {
  return (
    <html lang="en"><body>
      <div className="container">
        <h1>File Upload Demo</h1>
        {children}
      </div>
    </body></html>
  );
}
