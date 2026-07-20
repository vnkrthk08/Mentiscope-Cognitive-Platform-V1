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
    console.log("[Auth API] POST /auth/student/register", data);
    await new Promise((resolve) => setTimeout(resolve, 800)); // Simulate API response latency

    const newUser: User = {
      ...data,
      id: `stud_${Math.random().toString(36).substring(2, 11)}`,
      role: UserRole.STUDENT,
      token: "jwt_student_mock_token_xyz"
    };

    this.saveUserSession(newUser);
    return newUser;
  }

  static async studentLogin(email: string, rememberMe?: boolean): Promise<User> {
    console.log("[Auth API] POST /auth/student/login", { email, rememberMe });
    await new Promise((resolve) => setTimeout(resolve, 600));

    // Simple simulation: creates a student profile
    const user: User = {
      id: "stud_demo_123",
      name: "Alex Mercer",
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
      token: "jwt_student_mock_token_xyz"
    };

    this.saveUserSession(user);
    return user;
  }

  static async internLogin(emailOrId: string, passwordString: string): Promise<User> {
    console.log("[Auth API] POST /auth/intern/login", { emailOrId });
    await new Promise((resolve) => setTimeout(resolve, 600));

    // Standard demo intern credentials
    const user: User = {
      id: "intern_demo_456",
      name: "Dr. Clara Oswald",
      email: emailOrId.includes("@") ? emailOrId : "clara@mentiscope.org",
      role: UserRole.INTERN,
      token: "jwt_intern_mock_token_abc"
    };

    // Store in session
    this.saveUserSession(user);
    return user;
  }

  static async adminLogin(emailString: string, passwordString: string): Promise<User> {
    console.log("[Auth API] POST /auth/admin/login", { emailString });
    await new Promise((resolve) => setTimeout(resolve, 600));

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
