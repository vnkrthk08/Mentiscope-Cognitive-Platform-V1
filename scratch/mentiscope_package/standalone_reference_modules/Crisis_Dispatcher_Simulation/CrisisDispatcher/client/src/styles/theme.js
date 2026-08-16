import { theme as antTheme } from 'antd';

const theme = {
  algorithm: antTheme.darkAlgorithm,
  token: {
    colorPrimary: '#FF4D4F',
    colorSuccess: '#00E676',
    colorWarning: '#FFC400',
    colorError: '#FF1744',
    colorInfo: '#00B0FF',
    borderRadius: 12,
    fontFamily: "'Outfit', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    colorBgLayout: '#0A0F1E',
    colorBgContainer: '#131A2D',
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
  },
  components: {
    Layout: {
      siderBg: '#050811',
      headerBg: '#0A0F1E',
      bodyBg: '#0A0F1E',
    },
    Menu: {
      darkItemBg: '#050811',
      darkItemSelectedBg: 'rgba(255, 77, 79, 0.15)',
      darkItemHoverBg: '#111827',
      darkItemColor: '#8A99AF',
      darkItemSelectedColor: '#FF4D4F',
    },
    Card: {
      borderRadiusLG: 16,
    },
    Button: {
      borderRadius: 10,
      controlHeight: 44,
      fontWeight: 600,
    },
    Input: {
      borderRadius: 10,
      controlHeight: 44,
    },
    Table: {
      borderRadius: 16,
    },
    Segmented: {
      borderRadius: 10,
    }
  },
};

export default theme;
