import { readFile } from 'node:fs/promises';
import { validateConfig } from '../src/config.js';

export const rawConfig = JSON.parse(await readFile(new URL('../config.json', import.meta.url), 'utf8'));
export const config = validateConfig(rawConfig);
export const floors = config.floors;
