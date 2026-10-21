export const feelings = ['Very unpleasant', 'Unpleasant', 'Neutral', 'Pleasant', 'Very pleasant']
export const colors = [
  { name: 'Sage', value: '#8fa98d' }, { name: 'Rose', value: '#b98998' },
  { name: 'Sand', value: '#d1ad71' }, { name: 'Sky', value: '#789bb8' }, { name: 'Lavender', value: '#a399bb' },
]
export const pointSummary = (pleasantness, energy) => `${pleasantness === 0 ? 'Neutral pleasantness' : pleasantness > 0 ? 'Pleasant' : 'Unpleasant'} · ${energy === 0 ? 'Middle energy' : energy > 0 ? 'High energy' : 'Low energy'}`
