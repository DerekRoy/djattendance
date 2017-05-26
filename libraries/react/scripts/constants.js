import { addDays, differenceInWeeks, startOfWeek } from 'date-fns'

//constants

export const ATTENDANCE_MONITOR_GROUP = 4

export const ATTENDANCE_STATUS = [
  {id: 'P', name: 'Present'},
  {id: 'A', name: 'Absent'},
  {id: 'T', name: 'Tardy'},
  {id: 'U', name: 'Uniform'},
  {id: 'L', name: 'Left Class'},
]

export const ATTENDANCE_STATUS_LOOKUP = {
    'P': 'present',
    'A': 'absent',
    'T': 'tardy',
    'U': 'uniform',
    'L': 'left-class'
}

export const SLIP_STATUS_LOOKUP = {
    'A': 'approved',
    'P': 'pending',
    'F': 'fellowship',
    'D': 'denied',
    'S': 'approved' //by TA sister
}

export const GROUP_SLIP_TYPES = [
  {id: 'SICK', name: 'Sickness'},
  {id: 'SERV', name: 'Service'},
  {id: 'FWSHP', name: 'Fellowship'},
  {id: 'INTVW', name: 'Interview'},
  {id: 'GOSP', name: 'Gospel'},
  {id: 'CONF', name: 'Conference'},
  {id: 'WED', name: 'Wedding'},
  {id: 'FUNRL', name: 'Funeral'},
  {id: 'SPECL', name: 'Special'},
  {id: 'OTHER', name: 'Other'},
  {id: 'EMERG', name: 'Family Emergency'},
  {id: 'NOTIF', name: 'Notification Only'},
]

export const SLIP_TYPES = [
  ...GROUP_SLIP_TYPES,
  {id: 'NIGHT', name: 'Night Out'},
  {id: 'MEAL', name: 'Meal Out'},
]

export const TA_IS_INFORMED = {'id': 'true', 'name': 'TA informed'}

export const INFORMED = [
  TA_IS_INFORMED,
  {id: 'false', name: 'Did not inform training office'},
  {id: 'texted', name: 'Texted attendance number (for sisters during non-front office hours only)'},
]

export const SLIP_TYPE_LOOKUP = {
    'CONF': 'Conference',
    'EMERG': 'Family Emergency',
    'FWSHP': 'Fellowship',
    'FUNRL': 'Funeral',
    'GOSP': 'Gospel',
    'INTVW': 'Grad School/Job Interview',
    'GRAD': 'Graduation',
    'MEAL': 'Meal Out',
    'NIGHT': 'Night Out',
    'OTHER': 'Other',
    'SERV': 'Service',
    'SICK': 'Sickness',
    'SPECL': 'Special',
    'WED': 'Wedding',
    'NOTIF': 'Notification Only'
}

export const FA_ICON_LOOKUP = {
    "pending": "circle-thin",
    "denied": "minus-circle",
    "approved": "check-circle",
    "fellowship": "exclamation-circle"
}

export function joinValidClasses(classes) {
  return classes.filter((c) => c).join(' ');
};

export function categorizeEventStatus(wesr) {
  let status = {}

  let slip = wesr.slip || {}
  let gslip = wesr.gslip || {}
  let statuses = [slip.status, gslip.status]
  if (statuses.includes('P')) {
    status.slip = 'pending'
  } else if (statuses.includes('D')) {
    status.slip = 'denied'
  } else if (statuses.includes('F')) {
    status.slip = 'fellowship'
  } else if (statuses.includes('A') || statuses.includes('S')) {
    status.slip = 'approved'
    status.roll = 'excused'
    return status
  }

  if (!wesr.roll) {
    return status;
  } else if(wesr.roll.status === "A") {
    status.roll = 'absent'
  } else if(['T', 'U', 'L'].includes(wesr.roll.status)) {
    status.roll = 'tardy'
  }

  return status
}

export function canSubmitRoll(dateDetails) {
  let weekStart = dateDetails.weekStart
  let weekEnd = addDays(dateDetails.weekEnd, 1)
  let rollDate = new Date()
  return (rollDate >= weekStart && rollDate <= weekEnd)
}

// this is necessary because Roll.date and Event dates are given as Date, not Datetime, from django
export function getDateWithoutOffset(dateWithOffset) {
  let millsecsInMinute = 60000
  let dateWithoutOffset = new Date(dateWithOffset.getTime() + dateWithOffset.getTimezoneOffset() * 60000)
  return dateWithoutOffset
}

export function canFinalizeRolls(rolls, dateDetails) {
  let weekStart = dateDetails.weekStart
  let weekEnd = dateDetails.weekEnd
  let isWeekFinalized = rolls.filter(function(roll) {
    let rollDate = getDateWithoutOffset(new Date(roll.date))
    return rollDate >= weekStart && rollDate <= weekEnd && roll.finalized
  }).length > 0
  let now = new Date()
  // Monday midnight is when you can begin finalizing
  let isPastMondayMidnight = now >= weekEnd
  // Tuesday midnight is when you can no longer finalize
  weekEnd = addDays(weekEnd, 1)
  let isBeforeTuesdayMidnight = now <= weekEnd
  let canFinalizeWeek = !isWeekFinalized && isPastMondayMidnight && isBeforeTuesdayMidnight
  return canFinalizeWeek
}

export const compareLeaveslipEvents = (e1, e2) => {
  return new Date(e1.date) < new Date(e2.date) ? -1 : 1
}

export const compareEvents = (e1, e2) => {
  return new Date(e1.start_datetime) < new Date(e2.start_datetime) ? -1 : 1
}

export const compareLeaveslips = (ls1, ls2) => {
  let ls1Date = new Date(ls1.events.sort(compareLeaveslipEvents).slice(-1)[0].date)
  let ls2Date = new Date(ls2.events.sort(compareLeaveslipEvents).slice(-1)[0].date)
  return ls1Date < ls2Date ? -1 : 1
}

export function lastLeaveslip(leaveslips, type, status) {
  let matchingSlips = leaveslips.filter((ls) => {
    return ls.status == status && ls.type == type
  })
  return matchingSlips.sort(compareLeaveslips).slice(-1)[0]
}

export function getPeriodFromDate(term, date) {
  return Math.floor(
    differenceInWeeks(
      startOfWeek(date, {weekStartsOn: 1}),
      new Date(term.start)
    ) / 2
  )
}


export const taInformedToServerFormat = ta_informed => {
  if (ta_informed.id == "texted") {
    return {
      texted: true,
      informed: false,
    }
  } else if (ta_informed.id != "true") {
    return {
      texted: false,
      informed: false,
    }
  } else {
    return {
      informed: true,
      texted: false,
    }
  }
}
