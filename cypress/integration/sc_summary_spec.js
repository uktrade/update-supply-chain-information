import govDepartments from '../fixtures/govDepartment.json'
import supplyChains from '../fixtures/supplyChains.json'
import users from '../fixtures/user.json'

const govDepartment = govDepartments[0].fields
const supplyChain = supplyChains[0]
const user = users[0].fields

describe('Supply chain summary page', () => {
  it('successfully loads', () => {
    cy.visit(
      Cypress.config('baseUrl') +
      `/${supplyChain.fields.slug}/summary`
    )
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
      .contains(`${supplyChain.fields.name}`)
      .should('have.attr', 'href')
      .and('eq', `/${supplyChain.fields.slug}`)
    cy.get('li')
      .contains(`Full details of ${supplyChain.fields.name}`)
      .should('have.attr', 'href')
      .and('eq', `#`)
  })
  it('displays the header', () => {
    cy.get('h1').contains(`Summary of ${supplyChain.fields.name}`)
  })
  it('displays 5 accordian sections with a heading', () => {
    const headers = [
      'Key information',
      'Vulnerability assessment',
      'Scenario assessment',
      'Maturity self assessment',
      'Risk monitoring'
    ]

    cy.get('#accordion-default').should('have.length', 1)
    cy.get('.govuk-accordion__section')
      .should('have.length', 5)
      .each(($el, index) => {
        cy.wrap($el).contains(`${headers[index]}`)
      })
  })

  it('displays correct table values', () => {
    const table = cy
      .get('.govuk-accordion__section-content > dl')
      .first()
      .children()

    table.should('have.length', 4)
    const tableElement = '.govuk-summary-list__row'
    const editLabel = 'Change'

    cy.forms.checkSummaryTableContent(
      table,
      tableElement,
      0,
      'The contact for this supply chain',
      supplyChain.fields.contact_name,
      editLabel
    )

    cy.forms.checkSummaryTableContent(
      table,
      tableElement,
      1,
      'The email for the supply chain contact',
      supplyChain.fields.contact_email,
      editLabel
    )

    cy.forms.checkSummaryTableContent(
      table,
      tableElement,
      2,
      String.raw`The current vulnerability status is 'Low'. Is this accurate?`,
      'No' + ' ' + supplyChain.fields.vulnerability_status_disagree_reason,
      editLabel
    )


    cy.forms.checkSummaryTableContent(
      table,
      tableElement,
      3,
      String.raw`The current risk severity level is 'Medium'. Is this accurate?`,
      'Yes',
      editLabel
    )
  })
  it('opens all sections when open all is clicked', () => {
    cy.contains('Open all').click()
    cy.get('div > .govuk-accordion__section-content')
      .should('be.visible')
      .and('have.length', 5)
  })
  it('closes all sections when close all is clicked', () => {
    cy.contains('Close all').click()
    cy.get('div > .govuk-accordion__section-content').should('not.be.visible')
  })
  it('opens a section when the + symbol is clicked', () => {
    cy.get('#accordion-default-heading-1')
      .click()
    cy.get('#accordion-default-content-1').should('be.visible')
  })
  it('closes a section when the - symbol is clicked', () => {
    cy.get('#accordion-default-heading-1')
      .click()
    cy.get('#accordion-default-content-1').should('be.not.visible')
  })
  it('takes user to task list when button is clicked', () => {
    cy.get('a').contains('Back to task list').click()
    cy.url().should(
      'eq',
      Cypress.config('baseUrl') + `/${supplyChain.fields.slug}`
    )
  })
})
