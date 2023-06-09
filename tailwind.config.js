/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: ["./app/**/*.py",
            "./node_modules/flowbite/**/*.{js,jsx,ts,tsx}",
            "./node_modules/flowbite-react/**/*.{js,jsx,ts,tsx}",
          ],
  theme: {
    colors:{
      "gray1": "#F5F7F5",
      "gray2": "#7885A7",
      "blue1": "#243863",
      "pink1": "#AC435B",
      "dark1": "#1D131E",
      
    },
    extend: {},
  },
  plugins: [
    require("flowbite/plugin")
  ],
}
