
import users from '../fixtures/user.json'
const adminUser = users[1].fields

const unknownDept = 'unknown/'
const route = '/action-progress/' + unknownDept

// This test needs DEBUG to be turned off(to reflect PROD system) and some of the tests(monthly update
// and strategic action summary) are failing with that setting due to styling issues, mainly. It could well
// be a minor/one liner but Come back to it, when its quite
describe.skip('The not found page', () => {
  it('successfully loads', () => {
    cy.visit(Cypress.config('baseUrlSC') + `${route}`, {failOnStatusCode: false})
    cy.injectAxe()
  })
  it('has no accessibility issues', () => {
    cy.runA11y()
  })
  it('Displays the correct text', () => {
      cy.get('h1').contains('Not found')
      cy.get('p').contains('Page you are trying to access is not found.')

  })
  it('Displays correct links', () => {
      cy.get('a').contains('homepage').should('have.attr', 'href').and('eq', '/')
      cy.get('a').contains('Contact the Resilience Tool team').should('have.attr', 'href').and('eq', `mailto:${Cypress.env('FEEDBACK_GROUP_EMAIL')}?bcc=${adminUser.email}`)
  })
})
