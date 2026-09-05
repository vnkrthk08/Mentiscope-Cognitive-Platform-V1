import { User, UserRole } from "../../types";

const AUTH_USER_KEY = "mentiscope_auth_user";

export class AuthService {
  static getCurrentUser(): User | null {
    const saved = localStorage.getItem(AUTH_USER_KEY);
    if (!saved) return null;
    try {
      return JSON.parse(saved) as User;
    } catch {
      return null;
    }
  }

  static saveUserSession(user: User): void {
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
  }

  static logout(): void {
    localStorage.removeItem(AUTH_USER_KEY);
    // Also clean up assessment session state
    localStorage.removeItem("mentiscope_assessment_session");
  }

  static async studentRegister(data: Omit<User, "id" | "role"> & { consent: boolean }): Promise<User> {
    console.log("[Auth API] POST /api/auth/register", data);
    const res = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    if (!res.ok) {
      const errPayload = await res.json().catch(() => null);
      const msg = errPayload?.detail || errPayload?.error || "Registration failed. Please try again.";
      throw new Error(msg);
    }

    const user = await res.json();
    const fullUser: User = {
      ...user,
      role: UserRole.STUDENT
    };
    this.saveUserSession(fullUser);
    return fullUser;
  }

  static async studentLogin(email: string, rememberMe?: boolean): Promise<User> {
    console.log("[Auth API] POST /api/auth/login", { email, rememberMe });
    const cleanEmail = (email || "").trim().toLowerCase();
    if (!cleanEmail || !cleanEmail.includes("@")) {
      throw new Error("Please enter a valid student email address.");
    }

    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: cleanEmail, rememberMe })
    });

    if (!res.ok) {
      const errPayload = await res.json().catch(() => null);
      const msg = errPayload?.detail || errPayload?.error || "Account not found. Please check your email or create a new account to take the test.";
      throw new Error(msg);
    }

    const user = await res.json();
    const fullUser: User = {
      ...user,
      role: UserRole.STUDENT
    };
    this.saveUserSession(fullUser);
    return fullUser;
  }

  static async updateProfile(user: User): Promise<User> {
    console.log("[Auth API] POST /api/auth/profile", user);
    try {
      const res = await fetch("/api/auth/profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(user)
      });
      if (res.ok) {
        const updated = await res.json();
        const fullUser: User = {
          ...updated,
          role: user.role
        };
        this.saveUserSession(fullUser);
        return fullUser;
      }
    } catch (e) {
      console.warn("Backend profile update fallback:", e);
    }

    this.saveUserSession(user);
    return user;
  }



  static async adminLogin(emailString: string, passwordString: string): Promise<User> {
    console.log("[Auth API] POST /auth/admin/login", { emailString });
    await new Promise((resolve) => setTimeout(resolve, 600));

    // Valid admin passwords
    const validPasswords = ["admin123", "AdminPass123", "Admin@123"];
    if (!validPasswords.includes(passwordString)) {
      throw new Error("Invalid Super Admin password. (Demo password: admin123)");
    }

    const user: User = {
      id: "admin_demo_999",
      name: "Super Administrator",
      email: emailString,
      role: UserRole.SUPER_ADMIN,
      token: "jwt_admin_mock_token_super"
    };

    this.saveUserSession(user);
    return user;
  }

  static async requestForgotPassword(email: string): Promise<boolean> {
    console.log("[Auth API] POST /auth/forgot-password", { email });
    await new Promise((resolve) => setTimeout(resolve, 500));
    return true;
  }

  static async requestResetPassword(token: string, newPass: string): Promise<boolean> {
    console.log("[Auth API] POST /auth/reset-password", { token });
    await new Promise((resolve) => setTimeout(resolve, 500));
    return true;
  }
}
