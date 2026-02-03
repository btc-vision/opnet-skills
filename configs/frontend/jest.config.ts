module.exports = {
  //transform: {'^.+\\.ts?$': 'ts-jest'},
  transform:  { '^.+\\.(ts|tsx)?$': ['ts-jest', { diagnostics: { ignoreCodes: ['TS151001'] } }] },
  testEnvironment: 'node',
  testRegex: '/tests/.*\\.(test|spec)?\\.(ts|tsx)$',
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node']
};
