import users from '../fixtures/user.json'
import govDepartments from '../fixtures/govDepartment.json'
import supplyChains from '../fixtures/supplyChains.json'
import strategicActions from '../fixtures/strategicActions.json'
import updates from '../fixtures/strategicActionUpdates.json'

const user = users[0].fields
const govDepartment = govDepartments[0].fields
const supplyChain = supplyChains[4].fields
const strategicAction = strategicActions[9].fields
const update = updates[3].fields

describe('Strategic action update review page', () => {
  const route = `/${supplyChain.slug}/${strategicAction.slug}/updates/${update.slug}/review/`
  it('successfully loads', () => {
    cy.visit(Cypress.config('baseUrl') + route)
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
    cy.get('li').contains('Home').should('have.attr', 'href').and('eq', '/')
    cy.get('li')
      .contains(supplyChain.name)
      .should('have.attr', 'href')
      .and('eq', `/${supplyChain.slug}/`)
    cy.get('li')
      .contains(`Current monthly update for ${strategicAction.name}`)
      .should('have.attr', 'href')
      .and('eq', route)
  })
  it('displays the correct text', () => {
    cy.get('h1').contains(`Current monthly update for ${strategicAction.name}`)
    cy.get('div').contains(
      `Update submitted on `
    )
  })
  it('displays correct table values', () => {
    const table = cy
      .get('dl')
      .first()
      .children()

    table.should('have.length', 3)
    const tableElement = '.govuk-summary-list__row'

    cy.forms.checkSummaryTableContent(
      table,
      tableElement,
      0,
      'Latest monthly update',
      update.content
    )

    cy.forms.checkSummaryTableContent(
      table,
      tableElement,
      1,
      'Estimated date of completion',
      '1 February 2024'
    )

    cy.forms.checkSummaryTableContent(
      table,
      tableElement,
      2,
      'Current delivery status',
      `Green`
    )
  })
  it('takes user to task list when button is clicked', () => {
    cy.get('a').contains('Back').click()
    cy.url().should(
      'eq',
      Cypress.config('baseUrl') + `/${supplyChain.slug}/`
    )
  })
})

