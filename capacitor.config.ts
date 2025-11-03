import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.calorieai.app',
  appName: 'CalorieAI',
  webDir: 'dist',
  server: {
    androidScheme: 'https'
  }
};

export default config;
