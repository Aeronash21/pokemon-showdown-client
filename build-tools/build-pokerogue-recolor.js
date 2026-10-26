#!/usr/bin/env node
/**
 * Builds play.pokemonshowdown.com/style/pokerogue-recolor.css: Showdown's own stylesheets,
 * recoloured to PokéRogue's palette.
 *
 *     node build-tools/build-pokerogue-recolor.js
 *
 * Showdown's UI is mostly greys and greyish blues. This copies every colour-related
 * declaration (colours, backgrounds, borders, shadows) from the stylesheets the client
 * loads, in the order it loads them, and moves those greys and greyish blues to
 * PokéRogue's lilac/plum hue, keeping their lightness. Actual colours (type colours,
 * HP bars, links, warnings) are left as they are, and so is everything in rules for
 * types, statuses, battle effects and coloured notices (KEEP).
 * Because every declaration of those properties is copied in its original order, the
 * cascade between them stays the same; style/pokerogue-theme.css (loaded after this)
 * then styles the main pieces by hand.
 *
 * Run it again after changing any of the stylesheets below.
 */
'use strict';

const fs = require('fs');
const path = require('path');

const STYLE = path.join(__dirname, '..', 'play.pokemonshowdown.com', 'style');
// in the order testclient-old.html loads them (battle.css @imports battle-log.css first)
const SOURCES = ['battle-log.css', 'battle.css', 'oldclient.css', 'sim-types.css', 'utilichart.css'];
const OUT = path.join(STYLE, 'pokerogue-recolor.css');

const PLUM_HUE = 278;
/** Colours that mean something (types, status, effects, coloured notices) are copied unchanged */
const KEEP = /type|tint-|broadcast-|message-announce|message-effect|alt-notifying|sidecondition|weather|terrain|hpbar|status|\.(brn|par|slp|frz|psn|tox)\b/i;
const PROPS = /^(color|background|border(?!-radius|-collapse|-spacing|-image)|outline|box-shadow|text-shadow|caret-color|text-decoration-color|column-rule|fill|stroke)/i;

/*********************************************************
 * Colours
 *********************************************************/

function toHsl(r, g, b) {
	r /= 255; g /= 255; b /= 255;
	const max = Math.max(r, g, b), min = Math.min(r, g, b);
	const l = (max + min) / 2;
	if (max === min) return [0, 0, l];
	const d = max - min;
	const s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
	let h;
	if (max === r) h = (g - b) / d + (g < b ? 6 : 0);
	else if (max === g) h = (b - r) / d + 2;
	else h = (r - g) / d + 4;
	return [h * 60, s, l];
}
function toRgb(h, s, l) {
	const c = (1 - Math.abs(2 * l - 1)) * s;
	const x = c * (1 - Math.abs((h / 60) % 2 - 1));
	const m = l - c / 2;
	const [r, g, b] = h < 60 ? [c, x, 0] : h < 120 ? [x, c, 0] : h < 180 ? [0, c, x] :
		h < 240 ? [0, x, c] : h < 300 ? [x, 0, c] : [c, 0, x];
	return [r, g, b].map(v => Math.round((v + m) * 255));
}

/** Greys and greyish blues move to PokéRogue's plum hue; anything else stays. */
function recolor(r, g, b) {
	const [h, s, l] = toHsl(r, g, b);
	if (l > 0.97 || l < 0.04) return null; // white and black stay
	const grey = s < 0.08;
	const greyishBlue = h >= 180 && h <= 235 && s < 0.55;
	if (!grey && !greyishBlue) return null;
	// PokéRogue's surfaces: lilac #ece6f1 (s 26%) when light, plum #362d3e (s 16%) when dark
	const sat = grey ? (l > 0.6 ? 0.16 : 0.14) : Math.min(Math.max(s, 0.14), 0.32);
	return toRgb(PLUM_HUE, sat, l);
}

const hex2 = n => n.toString(16).padStart(2, '0');
const NAMED = {
	gray: [128, 128, 128], grey: [128, 128, 128], silver: [192, 192, 192], darkgray: [169, 169, 169],
	darkgrey: [169, 169, 169], lightgray: [211, 211, 211], lightgrey: [211, 211, 211], gainsboro: [220, 220, 220],
	whitesmoke: [245, 245, 245], dimgray: [105, 105, 105], dimgrey: [105, 105, 105],
};

function recolorValue(value) {
	if (/url\(/i.test(value) && !/gradient/i.test(value)) {
		// keep image URLs exactly; only touch colours outside url(...)
		return value.replace(/(url\([^)]*\))|([^u]+|u)/gi, (m, url, rest) => url ? url : recolorValue(rest));
	}
	return value
		.replace(/#([0-9a-f]{8}|[0-9a-f]{6}|[0-9a-f]{3,4})\b/gi, (m, hex) => {
			let h = hex;
			if (h.length <= 4) h = h.split('').map(c => c + c).join('');
			const [r, g, b] = [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16));
			const out = recolor(r, g, b);
			if (!out) return m;
			return '#' + out.map(hex2).join('') + (h.length === 8 ? h.slice(6) : '');
		})
		.replace(/rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(,\s*[\d.]+\s*)?\)/gi, (m, r, g, b, a) => {
			const out = recolor(+r, +g, +b);
			if (!out) return m;
			return a ? `rgba(${out.join(',')}${a.replace(/\s/g, '')})` : `rgb(${out.join(',')})`;
		})
		.replace(/hsla?\(\s*([\d.]+)\s*,\s*([\d.]+)%\s*,\s*([\d.]+)%\s*(,\s*[\d.]+\s*)?\)/gi, (m, h, s, l, a) => {
			const [r, g, b] = toRgb(+h % 360, +s / 100, +l / 100);
			const out = recolor(r, g, b);
			if (!out) return m;
			return a ? `rgba(${out.join(',')}${a.replace(/\s/g, '')})` : `rgb(${out.join(',')})`;
		})
		.replace(/(^|[\s,(])(gr[ae]y|silver|dark gr[ae]y|darkgr[ae]y|lightgr[ae]y|gainsboro|whitesmoke|dimgr[ae]y)(?=$|[\s,)!;])/gi, (m, pre, name) => {
			const rgb = NAMED[name.toLowerCase()];
			const out = rgb && recolor(...rgb);
			return out ? pre + '#' + out.map(hex2).join('') : m;
		});
}

/*********************************************************
 * A small CSS reader (enough for Showdown's stylesheets)
 *********************************************************/

function stripComments(css) {
	let out = '';
	let quote = '';
	for (let i = 0; i < css.length; i++) {
		const c = css[i];
		if (quote) {
			out += c;
			if (c === '\\') { out += css[++i] || ''; continue; }
			if (c === quote) quote = '';
		} else if (c === '"' || c === "'") {
			quote = c; out += c;
		} else if (c === '/' && css[i + 1] === '*') {
			const end = css.indexOf('*/', i + 2);
			i = end < 0 ? css.length : end + 1;
		} else {
			out += c;
		}
	}
	return out;
}

/** Finds the next `stops` character that isn't inside quotes or parentheses. */
function scan(css, start, stops) {
	let depth = 0;
	let quote = '';
	for (let i = start; i < css.length; i++) {
		const c = css[i];
		if (quote) {
			if (c === '\\') i++;
			else if (c === quote) quote = '';
		} else if (c === '"' || c === "'") {
			quote = c;
		} else if (c === '(') {
			depth++;
		} else if (c === ')') {
			depth--;
		} else if (depth === 0 && stops.includes(c)) {
			return i;
		}
	}
	return css.length;
}

function parseBlock(css, i, nodes) {
	while (i < css.length) {
		const stop = scan(css, i, '{};');
		const prelude = css.slice(i, stop).trim();
		const c = css[stop];
		if (c === '}' || stop >= css.length) return stop + 1;
		if (c === ';') { i = stop + 1; continue; } // @import, @charset: nothing to copy
		if (/^@(media|supports)\b/i.test(prelude)) {
			const node = { type: 'at', prelude, children: [] };
			i = parseBlock(css, stop + 1, node.children);
			nodes.push(node);
		} else if (prelude.startsWith('@')) {
			i = skipBlock(css, stop + 1); // @keyframes, @font-face
		} else {
			const end = matchBrace(css, stop + 1);
			nodes.push({ type: 'rule', selector: prelude, decls: parseDecls(css.slice(stop + 1, end)) });
			i = end + 1;
		}
	}
	return i;
}
function matchBrace(css, i) {
	let depth = 1;
	for (; i < css.length; i++) {
		const j = scan(css, i, '{}');
		if (j >= css.length) return j;
		if (css[j] === '{') depth++;
		else if (--depth === 0) return j;
		i = j;
	}
	return i;
}
function skipBlock(css, i) {
	return matchBrace(css, i) + 1;
}
function parseDecls(body) {
	const decls = [];
	let i = 0;
	while (i < body.length) {
		const end = scan(body, i, ';');
		const decl = body.slice(i, end).trim();
		i = end + 1;
		const colon = decl.indexOf(':');
		if (colon < 0) continue;
		decls.push([decl.slice(0, colon).trim(), decl.slice(colon + 1).trim()]);
	}
	return decls;
}

/*********************************************************
 * Output
 *********************************************************/

function emit(nodes, indent = '') {
	let out = '';
	for (const node of nodes) {
		if (node.type === 'at') {
			const inner = emit(node.children, indent + '\t');
			if (inner) out += `${indent}${node.prelude} {\n${inner}${indent}}\n`;
			continue;
		}
		const decls = node.decls.filter(([prop]) => PROPS.test(prop));
		if (!decls.length) continue;
		const selector = node.selector.replace(/\s*\n\s*/g, ' ');
		const keep = KEEP.test(selector);
		out += `${indent}${selector} {` + decls.map(([prop, value]) => ` ${prop}: ${keep ? value : recolorValue(value)};`).join('') + ' }\n';
	}
	return out;
}

let out = `/* Generated by build-tools/build-pokerogue-recolor.js from ${SOURCES.join(', ')}: do not edit. */\n`;
for (const file of SOURCES) {
	const nodes = [];
	parseBlock(stripComments(fs.readFileSync(path.join(STYLE, file), 'utf8')), 0, nodes);
	out += `\n/* ${file} */\n${emit(nodes)}`;
}
fs.writeFileSync(OUT, out);
console.log(`wrote ${path.relative(process.cwd(), OUT)} (${Math.round(out.length / 1024)} KB)`);
