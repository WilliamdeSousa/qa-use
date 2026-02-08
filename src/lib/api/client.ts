import createClient from 'openapi-fetch'

import type { paths } from '@/lib/api/v1'

export type Client = ReturnType<typeof createClient<paths>>

const isLocalMode = process.env.BROWSER_USE_MODE === 'local'

export const client = createClient<paths>({
  baseUrl: isLocalMode
    ? (process.env.BROWSER_USE_LOCAL_URL ?? 'http://local-runner:8000')
    : 'https://api.browser-use.com/',
  headers: isLocalMode ? {} : { Authorization: `Bearer ${process.env.BROWSER_USE_API_KEY}` },
})
