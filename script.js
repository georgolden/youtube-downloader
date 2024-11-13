const splitMp4IfNeeded = require('./splitter');

async function main() {
    try {
        const outputFiles = await splitMp4IfNeeded(`./downloads/5272d3b6-57b4-481e-94f0-2d4c81f984d1_Joe Rogan Experience #2219 - Donald Trump.mp4`, 24, './downloads');
        console.log('Output files:', outputFiles);
    } catch (error) {
        console.error('Error:', error.message);
    }
}

main();
