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
    try {
      const res = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });
      if (res.ok) {
        const user = await res.json();
        const fullUser: User = {
          ...user,
          role: UserRole.STUDENT
        };
        this.saveUserSession(fullUser);
        return fullUser;
      }
    } catch (e) {
      console.warn("Backend auth register fallback:", e);
    }

    const newUser: User = {
      ...data,
      id: `stud_${Math.random().toString(36).substring(2, 11)}`,
      role: UserRole.STUDENT,
      token: "jwt_student_active_session"
    };

    this.saveUserSession(newUser);
    return newUser;
  }

  static async studentLogin(email: string, rememberMe?: boolean): Promise<User> {
    console.log("[Auth API] POST /api/auth/login", { email, rememberMe });
    if (!email || !email.includes("@")) {
      throw new Error("Please enter a valid student email address (e.g. candidate@mentiscope.org).");
    }

    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, rememberMe })
      });
      if (res.ok) {
        const user = await res.json();
        const fullUser: User = {
          ...user,
          role: UserRole.STUDENT
        };
        this.saveUserSession(fullUser);
        return fullUser;
      }
    } catch (e) {
      console.warn("Backend auth login fallback:", e);
    }

    const user: User = {
      id: `stud_${email.split("@")[0].toLowerCase().replace(/[^a-z0-9]/g, "_")}`,
      name: email.split("@")[0].replace(".", " ").replace(/\b\w/g, (c) => c.toUpperCase()),
      email: email,
      role: UserRole.STUDENT,
      age: 21,
      gender: "Male",
      state: "Tamil Nadu",
      district: "Chennai",
      education: "Undergraduate",
      course: "Bachelor of Science",
      specialization: "Cognitive Science",
      previousExamPercentage: 88,
      collegeType: "Private",
      token: "jwt_student_active_session"
    };

    this.saveUserSession(user);
    return user;
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
