import { readFileSync, writeFileSync } from 'fs';
import { execSync } from 'child_process';

const manifestPath = './manifest.json';
const versionsPath = './versions.json';

const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
const versions = JSON.parse(readFileSync(versionsPath, 'utf8'));

const currentVersion = manifest.version;
const [major, minor, patch] = currentVersion.split('.').map(Number);

// Increment patch version
manifest.version = `${major}.${minor}.${patch + 1}`;

// Update versions.json
versions[currentVersion] = {
    'minAppVersion': manifest.minAppVersion,
    'releaseDate': new Date().toISOString().split('T')[0]
};

// Write updated files
writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
writeFileSync(versionsPath, JSON.stringify(versions, null, 2));

// Create git tag
execSync(`git tag -a v${manifest.version} -m "Release v${manifest.version}"`); 