const { spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');

async function getVideoDuration(filePath) {
    return new Promise((resolve, reject) => {
        const process = spawn('ffprobe', [
            '-i', filePath,
            '-show_entries', 'format=duration',
            '-v', 'quiet',
            '-of', 'default=noprint_wrappers=1:nokey=1'
        ]);

        let output = '';
        process.stdout.on('data', (data) => output += data);

        process.on('close', (code) => {
            if (code === 0) {
                resolve(parseInt(output.split('.')[0]));
            } else {
                reject(new Error('Failed to get duration'));
            }
        });
    });
}

async function splitMp4IfNeeded(inputPath, maxSizeMB = 24, outputDir = '') {
    try {
        const stats = await fs.stat(inputPath);
        
        if (!stats.isFile()) {
            throw new Error('Input path is not a file');
        }

        if (path.extname(inputPath).toLowerCase() !== '.mp4') {
            throw new Error('Input file must be an MP4 file');
        }

        const fileSizeMB = stats.size / (1024 * 1024);
        if (fileSizeMB <= maxSizeMB) {
            return [inputPath];
        }

        outputDir = outputDir || path.dirname(inputPath);
        await fs.mkdir(outputDir, { recursive: true });

        const fileName = path.basename(inputPath, '.mp4');
        const totalDuration = await getVideoDuration(inputPath);
        let currentDuration = 0;
        let partNumber = 1;
        const outputFiles = [];

        while (currentDuration < totalDuration) {
            const outputPath = path.join(outputDir, `${fileName}-${partNumber}.mp4`);
            
            await new Promise((resolve, reject) => {
                const args = [
                    '-i', inputPath,
                    '-ss', currentDuration.toString(),
                    '-c', 'copy',
                    '-fs', `${maxSizeMB * 1024 * 1024}`,
                    outputPath
                ];

                const process = spawn('ffmpeg', args);
                let errorOutput = '';

                process.stderr.on('data', (data) => {
                    errorOutput += data.toString();
                });

                process.on('close', async (code) => {
                    if (code === 0) {
                        resolve();
                    } else {
                        reject(new Error(`FFmpeg process failed with code ${code}\nFFmpeg output: ${errorOutput}`));
                    }
                });

                process.on('error', reject);
            });

            const partDuration = await getVideoDuration(outputPath);
            if (partDuration === 0) {
                break;  // Stop if we get a zero-duration file
            }

            outputFiles.push(outputPath);
            currentDuration += partDuration;
            partNumber++;
        }

        return outputFiles;
    } catch (error) {
        if (error.code === 'ENOENT' && error.path === inputPath) {
            throw new Error('Input file does not exist');
        }
        throw error;
    }
}

module.exports = splitMp4IfNeeded;
