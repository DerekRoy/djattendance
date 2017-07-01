import React, { Component } from 'react'
import { Button } from 'react-bootstrap'

const SlipTitle = (props) => {
  let actionText = props.form.id ? 'Edit' : 'Submit'
  return (
    <h4 className='dt-leaveslip__title'>
      {actionText + ' Leaveslip'}&nbsp;
      {props.form.id && <Button onClick={props.resetForm} className="pull-right" bsSize="small">New Leaveslip</Button>}
    </h4>
  )
}

export default SlipTitle
