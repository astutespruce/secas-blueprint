import { hasWindow, saveToStorage, encodeParams } from 'util/dom'
import { captureException } from 'util/log'
import config from '../../../gatsby-config'

const {
  apiToken,
  msFormURL,
  msFormEmail,
  msFormName,
  msFormOrg,
  msFormUse,
  msFormAreaName,
  msFormFileName,
} = config.siteMetadata
let { apiHost } = config.siteMetadata

const pollInterval = 1000 // milliseconds; 1 second
const jobTimeout = 600000 // milliseconds; 10 minutes

if (hasWindow && !apiHost) {
  apiHost = `//${window.location.host}`
}

const API = `${apiHost}/api/reports`

export const uploadFile = async (file, name, onProgress) => {
  // NOTE: both file and name are required by API
  const formData = new FormData()
  formData.append('file', file)
  formData.append('name', name)

  const response = await fetch(`${API}/custom?token=${apiToken}`, {
    method: 'POST',
    body: formData,
  })

  const json = await response.json()
  const { job, detail } = json

  if (response.status === 400) {
    // indicates error with user request, show error to user

    // just for logging
    console.error('Bad upload request', json)
    captureException('Bad upload request', json)

    return { error: detail }
  }

  if (response.status !== 200) {
    console.error('Bad response', json)

    captureException('Bad upload response', json)

    throw new Error(response.statusText)
  }

  const result = await pollJob(job, onProgress)
  return result
}

export const createSummaryUnitReport = async (id, type, onProgress) => {
  let unitType = null

  if (type === 'subwatershed') {
    unitType = 'huc12'
  } else if (type === 'marine lease block') {
    unitType = 'marine_blocks'
  }

  const response = await fetch(`${API}/${unitType}/${id}?token=${apiToken}`, {
    method: 'POST',
  })

  const json = await response.json()
  const { job, detail } = json

  if (response.status === 400) {
    // indicates error with user request, show error to user

    // just for logging
    console.error('Bad create summary report request', json)
    captureException('Bad create summary report request', json)

    return { error: detail }
  }

  if (response.status !== 200) {
    console.error('Bad response', json)
    captureException('Bad upload response', json)

    throw new Error(response.statusText)
  }

  const result = await pollJob(job, onProgress)
  return result
}

const pollJob = async (jobId, onProgress) => {
  let time = 0

  while (time < jobTimeout) {
    const response = await fetch(`${API}/status/${jobId}`, {
      cache: 'no-cache',
    })

    const json = await response.json()
    const {
      status = null,
      progress = null,
      message = null,
      errors = null,
      detail: error = null, // error message
      result = null,
    } = json

    if (response.status != 200 || status === 'failed') {
      captureException('Report job failed', json)
      if (error) {
        return { error }
      }

      throw Error(response.statusText)
    }

    if (status === 'success') {
      return { result: `${apiHost}${result}`, errors }
    }

    if (progress != null) {
      onProgress({ progress, message, errors })
    }

    // sleep
    await new Promise((r) => setTimeout(r, pollInterval))
    time += pollInterval
  }

  // if we got here, it meant that we hit a timeout error
  captureException('Report job timed out')

  return {
    error:
      'timeout while creating report.  Your area of interest may be too big.',
  }
}

export const submitUserInfo = async (userInfo) => {
  const { userEmail, userName, userOrg, userUse } = userInfo

  // mapping of form fields to form field IDs in MS form
  const questionIds = {
    userEmail: msFormEmail,
    userName: msFormName,
    userOrg: msFormOrg,
    userUse: msFormUse,
    areaName: msFormAreaName,
    fileName: msFormFileName,
  }

  const answers = Object.entries(questionIds).map(([field, questionId]) => ({
    questionId,
    answer1: userInfo[field],
  }))

  try {
    // in no-cors mode, we can submit but not receive content
    await fetch(msFormURL, {
      method: 'POST',
      mode: 'no-cors',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: encodeParams({ answers: JSON.stringify(answers) }),
    })

    saveToStorage('reportForm', {
      userEmail,
      userName,
      userOrg,
      userUse,
    })
  } catch (ex) {
    console.error('Could not submit user info to MS Form', userInfo)
  }
}
