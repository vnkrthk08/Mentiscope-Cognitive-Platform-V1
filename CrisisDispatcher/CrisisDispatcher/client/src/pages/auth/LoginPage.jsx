import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Form, Input, Button, message, Segmented } from 'antd';
import { MailOutlined, LockOutlined, AlertOutlined } from '@ant-design/icons';
import { useAuth } from '../../contexts/AuthContext';

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const [role, setRole] = useState('Student');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      const userData = await login(values.email, values.password);
      message.success(`Welcome back, ${userData.name}!`);
      navigate(userData.role === 'admin' ? '/admin' : '/dashboard');
    } catch (error) {
      message.error(error.response?.data?.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-logo">
          <AlertOutlined style={{ fontSize: 40, color: '#DC3545', marginBottom: 8 }} />
          <h1>Crisis Dispatcher</h1>
          <p>Emergency Response Assessment Platform</p>
        </div>

        <Segmented
          block
          options={['Student', 'Admin']}
          value={role}
          onChange={setRole}
          style={{ marginBottom: 28 }}
        />

        <Form
          name="login"
          layout="vertical"
          onFinish={handleSubmit}
          autoComplete="off"
          requiredMark={false}
          initialValues={{
            email: role === 'Admin' ? 'admin@crisisapp.com' : '',
          }}
        >
          <Form.Item
            name="email"
            rules={[
              { required: true, message: 'Please enter your email' },
              { type: 'email', message: 'Please enter a valid email' },
            ]}
          >
            <Input
              prefix={<MailOutlined style={{ color: '#bbb' }} />}
              placeholder="Email address"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: 'Please enter your password' }]}
          >
            <Input.Password
              prefix={<LockOutlined style={{ color: '#bbb' }} />}
              placeholder="Password"
              size="large"
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 16 }}>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              size="large"
              style={{
                height: 48,
                fontSize: 16,
                fontWeight: 600,
                background: 'linear-gradient(135deg, #FF4D4F 0%, #FF7875 100%)',
                border: 'none',
              }}
            >
              Sign In
            </Button>
          </Form.Item>
        </Form>

        {role === 'Student' && (
          <div style={{ textAlign: 'center', marginTop: 8 }}>
            <span style={{ color: '#8A99AF' }}>Don&apos;t have an account? </span>
            <Link to="/register" style={{ fontWeight: 600, color: '#FF4D4F' }}>Register</Link>
          </div>
        )}
      </div>
    </div>
  );
}
