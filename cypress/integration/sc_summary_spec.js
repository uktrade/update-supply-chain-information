import govDepartments from '../fixtures/govDepartment.json'
import supplyChains from '../fixtures/supplyChains.json'
import users from '../fixtures/user.json'
import { urlBuilder } from "../support/utils.js"

const urls = urlBuilder();
const govDepartment = govDepartments[0].fields
const supplyChain = supplyChains.filter(sc => sc.fields.name == 'Supply Chain 1')[0]
const user = users[0].fields

describe.skip('Supply chain summary page', () => {
  it('successfully loads', () => {
    cy.visit(urls.summary)
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
    cy.get('li').contains('Home').should('have.attr', 'href').and('eq', '/')
  })
  it('displays the header', () => {
    cy.get('h1').contains('Supply chain summary')
  })

  it('displays correct table values', () => {
    const table = cy
      .get('dl')
      .first()
      .children()

    table.should('have.length', 4)

  })
  it('takes user to task list when button is clicked', () => {
    cy.get('a').contains('Back').click()
    cy.url().should(
      'eq',
      urls.home + '/'
    )
  })
})

describe.skip('Paginate Supply chains', () => {
  it('successfully loads', () => {
    cy.visit(urls.summary)
  })
  it('displays 5 supply chains in the table', () => {
    cy.get('.govuk-accordion__section').should('have.length', 5)
  })
  it('displays correct items in pagination list', () => {
    cy.get('.moj-pagination__list').find('li').should('have.length', 3)
    cy.get('.moj-pagination__item--active').contains('1')
    cy.get('.moj-pagination__item').contains('2')
    cy.get('.moj-pagination__item').contains('Next')
  })
  it('displays second page of supply chains after clicking Next', () => {
    cy.contains('Next').click()
    cy.url().should('eq', urls.summary + '?page=2')
    cy.get('.govuk-accordion__section').should('have.length', 4)
  })
  it('displays first page of supply chain after clicking Previous', () => {
    cy.contains('Previous').click()
    cy.url().should('eq', urls.summary + '?page=1')
  })
})
