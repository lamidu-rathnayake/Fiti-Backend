"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

export interface UserProfile {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
  role?: "client" | "seller";
}

interface AuthContextType {
  user: UserProfile | null;
  loading: boolean;
  loginAsClient: (name?: string) => void;
  loginAsSeller: (name?: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: false,
  loginAsClient: () => {},
  loginAsSeller: () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>({
    uid: "mock_firebase_uid",
    email: "adam@example.com",
    displayName: "Adam Wright",
    photoURL: null,
    role: "client",
  });
  const [loading, setLoading] = useState(false);

  const loginAsClient = (name = "Adam Wright") => {
    setUser({
      uid: "mock_firebase_uid",
      email: "adam@example.com",
      displayName: name,
      photoURL: null,
      role: "client",
    });
  };

  const loginAsSeller = (name = "Master Tailor") => {
    setUser({
      uid: "seller_firebase_uid_1",
      email: "atelier@savilerow.com",
      displayName: name,
      photoURL: null,
      role: "seller",
    });
  };

  const logout = () => {
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, loginAsClient, loginAsSeller, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
