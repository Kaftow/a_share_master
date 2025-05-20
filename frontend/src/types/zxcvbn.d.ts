declare module 'zxcvbn' {
  interface ZXCVBNResult {
    score: number; // 0-4
    feedback: {
      warning: string;
      suggestions: string[];
    };
  }
  function zxcvbn(password: string): ZXCVBNResult;
  export default zxcvbn;
}
