import users from '../fixtures/user.json'
import govDepartments from '../fixtures/govDepartment.json'
import supplyChains from '../fixtures/supplyChains.json'

const user = users[0].fields
const govDepartment = govDepartments[0].fields
const supplyChain = supplyChains[4].fields

describe('The Supply Chain TaskComplete Page', () => {
  it('successfully loads', () => {
    cy.visit(Cypress.config('baseUrl') + `/${supplyChain.slug}/complete/`)
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
      .contains('Update complete')
      .should('have.attr', 'href')
      .and('eq', `/${supplyChain.slug}/complete/`)
  })
  it('displays the correct text', () => {
    cy.get('h1').contains('Update complete')
    cy.get('div').contains(
      `Thank you for submitting your monthly update for the ${supplyChain.name} supply chain.`
    )
  })
  it('displays the correct inset text', () => {
    cy.get('h2 + p').invoke('text').should('match', /You have given updates for\s+\d+ of \d+ supply chains./)
  })
  it('displays the correct link back to home', () => {
    cy.get('p').contains(
      'You can go back and give an update for another supply chain.'
    )

    cy.get('#home').should('have.attr', 'href').and('equal', '/')
  })
})

const completedSC = supplyChains[1].fields

describe('Validate complete view for manual access', () => {
  it('successfully loads completed un-submitted Supply chain, by redirecting to tasklist page', () => {
    cy.visit(Cypress.config('baseUrl') + `/${completedSC.slug}/complete/`)
  })
  it('displays breadcrumbs', () => {
    cy.get('li').contains('Home').should('have.attr', 'href').and('eq', `/`)
    cy.get('li')
      .contains(completedSC.name)
      .should('have.attr', 'href')
      .and('eq', `/${completedSC.slug}/`)
  })
  it('displays the correct header', () => {
    cy.get('h1').contains(`Update ${completedSC.name}`)
    cy.get('div').contains(`Update complete`)
    cy.get('div').contains(`2 of 2 mandatory actions are complete.`)
  })
  it('displays correct table headers', () => {
    cy.get('thead').find('th').should('have.length', 2)
    cy.get('th').contains('Monthly strategic actions updates')
  })
  it('displays 2 strategic actions in the table', () => {
    cy.get('tbody').find('tr').should('have.length', 2)
    cy.get('tbody').find('td').should('have.length', 4)
    cy.get('td').contains('completed')
  })
  it('displays enabled submit button', () => {
    cy.get('form').find('button').should('be.enabled')
  })
})
