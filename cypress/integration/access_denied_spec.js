import supplyChains from '../fixtures/supplyChains.json'
import users from '../fixtures/user.json'

const supplyChain = supplyChains[7].fields
const adminUser = users[1].fields

describe('The access denied page', () => {
  it('successfully loads', () => {
    cy.visit(Cypress.config('baseUrl') + `/${supplyChain.slug}/`, {failOnStatusCode: false})
    cy.injectAxe()
  })
  it('has no accessibility issues', () => {
    cy.runA11y()
  })
  it('Displays the correct text', () => {
      cy.get('h1').contains('Access denied')
      cy.get('p').contains('You do not have permission to access this page.')
      cy.get('p').contains('Please try one of the following:')
      cy.get('ul').children().should('have.length', 4)
      cy.get('li').contains('If you typed the web address, check it is correct')
      cy.get('li').contains('If you pasted the web address, check you copied the entire address')
      cy.get('li').contains('Browse the homepage to find the information you need')
      cy.get('li').contains('Contact the Resilience Tool team if you think you do have permission to access this page.')
  })
  it('Displays correct links', () => {
      cy.get('a').contains('homepage').should('have.attr', 'href').and('eq', '/')
      cy.get('a').contains('Contact the Resilience Tool team').should('have.attr', 'href').and('eq', `mailto:${Cypress.env('FEEDBACK_GROUP_EMAIL')}?bcc=${adminUser.email}`)
  })
})
