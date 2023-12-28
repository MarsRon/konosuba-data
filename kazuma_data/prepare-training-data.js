import { readFileSync, writeFileSync } from 'fs'

const limit = 5000

const lines = readFileSync('./full-data.txt', 'utf8')

const dialogs = lines
  .match(/“.+?”/g)
  .map(line => line.slice(1, -1))
  .filter(line => !line.match(/^…+?$/))

const data = dialogs.slice(0, limit).join('\n')

console.log(`${dialogs.length} lines of dialog
${limit} lines as training data`)

writeFileSync('./training-data.txt', data)
