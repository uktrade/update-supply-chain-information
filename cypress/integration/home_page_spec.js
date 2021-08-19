import users from '../fixtures/user.json'
import govDepartments from '../fixtures/govDepartment.json'

const user = users[0].fields
const adminUser = users[1].fields
const govDepartment = govDepartments[0].fields

describe('The Home Page', () => {
  it('successfully loads', () => {
    cy.visit(Cypress.config('baseUrl'))
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
  it("displays the BETA phase banner with feedback link", () => {
    const bannerContents = cy.get('.govuk-phase-banner').children()
    bannerContents.get('.govuk-phase-banner__content__tag').contains('beta')
    bannerContents.get('.govuk-phase-banner__text').contains('This is a new service – your feedback will help us to improve it.')
    bannerContents.get('a').contains('feedback').should('have.attr', 'href').and('eq', `mailto:${Cypress.env('FEEDBACK_GROUP_EMAIL')}?bcc=${adminUser.email}`)
  })
  it('displays the correct text', () => {
    cy.get('h1').contains('UK supply chain')
    cy.get('h1').invoke('text').should('eq', 'UK supply chainresilience tool')

    cy.get('p').contains("Use this tool to help manage critical supply chain resilience across the UK.")

    cy.get('h2').contains('Supply chain information')

    cy.get('.govuk-grid-row > .govuk-grid-column-one-half > .govuk-list').children().should('have.length', 2)

    cy.get('a')
    .contains('Monthly update')
    .should('have.attr', 'href')
    .and('eq', `/supply-chains/`)

    cy.get('a')
    .contains('Strategic action progress')
    .should('have.attr', 'href')
    .and('eq', `/action-progress/`)
  })
})
