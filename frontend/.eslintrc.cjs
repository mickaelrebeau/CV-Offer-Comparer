module.exports = {
  root: true,
  env: { node: true, browser: true, es2022: true },
  extends: ['plugin:vue/vue3-essential', '@vue/eslint-config-typescript'],
  parserOptions: {
    ecmaVersion: 'latest',
  },
  overrides: [
    {
      // shadcn-vue style primitives: name matches the HTML tag on purpose.
      files: ['src/components/ui/**/*.{vue,ts}'],
      rules: {
        'vue/multi-word-component-names': 'off',
        'vue/no-reserved-component-names': 'off',
      },
    },
  ],
}
