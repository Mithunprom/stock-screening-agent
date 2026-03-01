import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/app/**/*.{ts,tsx}",
    "./src/components/**/*.{ts,tsx}",
    "./src/lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))"
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))"
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))"
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))"
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))"
        },
        fintech: {
          ink: "#0b1120",
          sand: "#f4f1ea",
          emerald: "#0f766e",
          amber: "#d97706",
          steel: "#94a3b8",
          berry: "#a21caf"
        }
      },
      boxShadow: {
        soft: "0 16px 40px rgba(15, 23, 42, 0.10)",
        card: "0 10px 30px rgba(15, 23, 42, 0.08)"
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.5rem"
      },
      fontFamily: {
        sans: ["var(--font-sans)"],
        display: ["var(--font-display)"]
      },
      backgroundImage: {
        "hero-glow":
          "radial-gradient(circle at 20% 20%, rgba(15,118,110,0.20), transparent 30%), radial-gradient(circle at 80% 10%, rgba(217,119,6,0.16), transparent 25%), linear-gradient(135deg, rgba(255,255,255,0.96), rgba(248,250,252,0.92))"
      }
    }
  },
  plugins: []
};

export default config;
