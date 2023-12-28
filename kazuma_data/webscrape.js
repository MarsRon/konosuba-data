import { JSDOM, VirtualConsole, ResourceLoader } from 'jsdom'
import fs from 'fs/promises'
import { performance } from 'perf_hooks'

const resourceLoader = new ResourceLoader({
  // Somehow proxies didn't work for me idk why
  // proxy: 'https://115.75.1.184:8118',
  strictSSL: false
})

process.on('uncaughtException', console.log)

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms))

const getDocument = async url => {
  const virtualConsole = new VirtualConsole()
  const dom = await JSDOM.fromURL(url, {
    virtualConsole,
    resources: resourceLoader
  })
  return dom.window.document
}

const readMainDirectory = async () => {
  console.log('Downloading main directory')
  const $ = await getDocument('https://cgtranslations.me/konosuba/')
  const links = [...$.querySelectorAll('a')]
    .map(e => e.getAttribute('href'))
    .filter(link =>
      link?.match(/cgtranslations.me\/\d{4}\/\d{2}\/\d{2}\/konosuba/)
    )
  return links
}

const downloadArticle = async (link, timeout) => {
  await sleep(timeout)
  const t1 = performance.now()

  const $ = await getDocument(link)
  const article = $.querySelector('.entry-content')
  const contentHTML = article.innerHTML.split('<hr>').at(-2)
  const content$ = new JSDOM(contentHTML).window.document
  const paragraphs = [...content$.querySelectorAll('p')]
  const contentText = paragraphs
    .map(e => e.textContent.trim())
    .filter(text => text)
    .join('\n')
    .replace(/\n{2,}/, '\n')
    .trim()

  const t2 = performance.now()
  console.log(`Downloaded ${link}: ${((t2 - t1) / 1000).toLocaleString()}s`)

  return contentText
}

readMainDirectory()
  .then(links =>
    Promise.all(
      links.map((link, index) =>
        downloadArticle(link, (index + Math.random()) * 1000)
      )
    )
  )
  .then(async contents => contents.join('\n'))
  .then(async content => content.replace(/<tl note:.*?>\n?/gi, ''))
  .then(content => {
    fs.writeFile('./full-data.txt', content)
    require('./prepare-training-data')
  })