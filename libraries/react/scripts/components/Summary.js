import React, { Component } from 'react'
import { Alert, Button } from 'react-bootstrap'

import SlipDetail from './SlipDetail'
import { FA_ICON_LOOKUP } from '../constants'

const Summary = ({...p}) => {
  let unexcused_absences=p.eventsRolls.filter(esr => esr.event.status.roll==='absent'&&esr.event.status.slip!=='approved')
  let unexcused_tardies=p.eventsRolls.filter(esr => esr.event.status.roll==='tardy'&&esr.event.status.slip!=='approved')
  const TARDY_LIMIT = 4
  const ABSENT_LIMIT = 1
  let tardies = unexcused_tardies.length
  let absences = unexcused_absences.length
  let tardyLifestudies = tardies > TARDY_LIMIT  ? tardies - TARDY_LIMIT + 1 : 0
  let absentLifestudies = absences > ABSENT_LIMIT ? absences - ABSENT_LIMIT + 1 : 0
  let slips = [...p.leaveslips, ...p.groupslips]

  return (
    <div>
      <h5 className="summary__lifestudies">
        LIFE STUDIES POSSIBLE: {tardyLifestudies + absentLifestudies}
      </h5>

      <h5>Leaveslips</h5>
      <div className="row summary__leaveslips">
        <div className="col-xs-2">Date</div>
        <div className="col-xs-1">State</div>
        <div className="col-xs-6">Event</div>
        <div className="col-xs-1">Reason</div>
      </div>
      {slips.map((slip, i) => <SlipDetail slip={slip} key={i} {...p} /> )}

      <Alert bsStyle="danger" className="dt-leaveslip__note">
        Note: Report information will not be up-to-date until attendance office hours (i.e., when the potential violators list is posted).
      </Alert>
    </div>
  )
}

Summary.propTypes = {
}

export default Summary
