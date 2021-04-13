import users from '../fixtures/user.json'
import strategicActions from '../fixtures/strategicActions.json'

const user = users[0].fields
const strategicActionPK = strategicActions[0].pk
const strategicAction = strategicActions[0].fields

describe('The new Monthly Update page', () => {
  it('successfully loads', () => {
    cy.visit(`http://localhost:8001/strategic-actions/${strategicActionPK}/update/start/`)
  })
  it('displays the correct page header', () => {
    cy.get('h1').contains(
      'Strategic action monthly update'
    )
    cy.get('h2:first').contains('Last update')
  })
  it('displays the previous update', () => {
    cy.get('h2:first').contains('Last update')
  })
  it('has a form', () => {
    cy.get('main').get('form').should().exist()
  })
})
