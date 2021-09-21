import users from '../fixtures/user.json'
import govDepartments from '../fixtures/govDepartment.json'

const user = users[0].fields
const govDepartment = govDepartments[0].fields

describe('Privacy notice Page', () => {
  it('successfully loads', () => {
    cy.visit(Cypress.config('baseUrlSC') + '/privacy-notice/')
    cy.injectAxe()
  })
  it('has no accessibility issues', () => {
    cy.runA11y()
  })
  it("displays user's name and department in header", () => {
    cy.get('.app-header-item').should(
      'have.text',
      `${user.first_name} ${user.last_name} - ${govDepartment.name}`
    )
  })
  it('displays breadcrumbs', () => {
    cy.get('ol').children().should('have.length', 1)
    cy.get('li').contains('Home').should('have.attr', 'href').and('eq', '/supply-chains/')
  })
  it('displays the correct header', () => {
    cy.get('h1').contains('Privacy notice for DIT clients')
  })
  it('displays the correct sub-headers', () => {
    cy.get('.govuk-heading-l').contains('The purpose of this document')
    cy.get('.govuk-heading-l').contains('What data we collect about you')
    cy.get('.govuk-heading-l').contains('Why we need your data and how we use it')
    cy.get('.govuk-heading-l').contains('Where do we obtain your information from?')
    cy.get('.govuk-heading-l').contains('Our legal basis for processing your data')
    cy.get('.govuk-heading-l').contains('How we may share your information')
    cy.get('.govuk-heading-l').contains('How long we keep your data')
    cy.get('.govuk-heading-l').contains('How we protect your data and keep it secure')
    cy.get('.govuk-heading-l').contains('Your rights')
    cy.get('.govuk-heading-l').contains('Accessibility')
    cy.get('.govuk-heading-l').contains('Contacting us')
    cy.get('.govuk-heading-l').contains('Changes to this privacy notice')
    cy.get('.govuk-heading-l').contains('Identity and contact details')

  })
  it('displays contact information', () => {
    cy.get('.contact-block').should('have.length', 4)
  })
  it('displays the correct link to top', () => {
    cy.get('a').contains(
      'Back to top'
    )
  })
  it('displays link to privacy notice in footer', () => {
    cy.get('a').contains('Privacy').should('have.attr', 'href').and('eq', '/supply-chains/privacy-notice/')
  })
})