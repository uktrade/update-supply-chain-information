import users from '../fixtures/user.json'
import govDepartments from '../fixtures/govDepartment.json'

const user = users[0].fields
const adminUser = users[1].fields
const govDepartment = govDepartments[0].fields

describe('The Supply Chain Home Page', () => {
  it('successfully loads', () => {
    cy.visit(Cypress.config('baseUrlSC'))
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
  it('displays breadcrumbs', () => {
    cy.get('ol').children().should('have.length', 1)
    cy.get('li').contains('Home').should('have.attr', 'href').and('eq', `/`)
  })
  it('displays the correct text', () => {
    cy.get('h1').contains(
      'Monthly update'
    )
    cy.get('p').contains("Keep your monthly action plan up to date so we can work towards constantly improving the UK's supply chain resilience.")
    cy.contains('Complete your monthly update').should('not.exist')
    cy.contains('Your monthly update is complete').should('not.exist')
    cy.get('li').invoke('text').should('match', /You need to complete your monthly update. Complete \d+ supply chains/)
    cy.lastWorkingDay().then(deadline => {
      cy.get('li:first-of-type').invoke('text').should('match', new RegExp(`\\s*You need to complete your monthly update. Complete \\d+ supply chains by\\s*${deadline}\\s*`))
    })
    cy.get('li').contains(
      'Select a supply chain to provide your regular monthly update.'
    )
    cy.get('p').contains(
      'All supply chains have been completed for this month'
    ).should('not.exist')

  })
  it('displays correct table headers', () => {
    cy.get('thead').find('th').should('have.length', 3)
    cy.get('th').contains('Supply chain')
    cy.get('th').contains('No. strategic actions')
    cy.get('th').contains('Last updated')
  })
  it('displays 5 supply chains in the table', () => {
    cy.get('tbody').find('tr').should('have.length', 5)
  })
  it('displays correct items in pagination list', () => {
    cy.get('.moj-pagination__list').find('li').should('have.length', 3)
    cy.get('.moj-pagination__item--active').contains('1')
    cy.get('.moj-pagination__item').contains('2')
    cy.get('.moj-pagination__item').contains('Next')
  })
  it('displays second page of supply chains after clicking Next', () => {
    cy.contains('Next').click()
    cy.url().should('eq', Cypress.config('baseUrlSC') + '/?page=2')
    cy.get('tbody').find('tr').should('have.length', 2)
  })
  it('displays first page of supply chains after clicking Previous', () => {
    cy.contains('Previous').click()
    cy.url().should('eq', Cypress.config('baseUrlSC') + '/?page=1')
  })
  it('displays button to go back', () => {
    cy.get('a')
      .contains('Back')
      .should('have.attr', 'href')
      .and('equal', '/')
  })
})
