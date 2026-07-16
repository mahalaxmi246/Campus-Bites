import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Navbar } from "./components/Navbar";
import { AuthProvider } from "./context/AuthContext";
import { LoginPage } from "./pages/LoginPage";
import { MenuPage } from "./pages/MenuPage";
import { RegisterPage } from "./pages/RegisterPage";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          {/* Menu browsing is public — matches the backend's GET /menu
              being unauthenticated. Login is only required at checkout
              (Week 4/5), not to browse. */}
          <Route path="/" element={<MenuPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}