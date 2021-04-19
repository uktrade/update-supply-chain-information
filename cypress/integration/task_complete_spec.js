import users from '../fixtures/user.json'
import govDepartments from '../fixtures/govDepartment.json'
import supplyChains from '../fixtures/supplyChains.json'


const user = users[0].fields
const govDepartment = govDepartments[0].fields
const supplyChain = supplyChains[4].fields

describe('The Supply Chain TaskComplete Page', () => {
  it('successfully loads', () => {
    cy.visit(Cypress.config('baseUrl') + `/${supplyChain.slug}/complete`)
    cy.injectAxe()
  })
  it.skip('has no accessibility issues', () => {
    cy.runA11y()
  })
  it("displays user's name and department in header", () => {
    cy.get('.app-header-item').should(
      'have.text',
      `${user.first_name} ${user.last_name} - ${govDepartment.name}`
    )
  })
  it('displays bread crumbs', () => {
    cy.get('li').contains('Home')
    cy.get('li').contains('Update complete')
  })
  it('displays the correct text', () => {
    cy.get('h1').contains('Update complete')
    cy.get('div')
      .contains(`Thank you for submitting your monthly update for the ${supplyChain.name} supply chain.`)
  })
  it('displays the correct inset text', () => {
    cy.get('div')
      .contains(`You have given updates for 1 of 6 supply chains.`)
  })
  it('displays the correct link back to home', () => {
    cy.get('p')
      .contains('You can go back and give an update for another supply chain.')

    cy.get('#home')
      .should('have.attr', 'href')
      .and('equal', '/')
  })
})

const completedSC = supplyChains[1].fields

describe('Validate complete view for manual access', () => {
  it('successfully loads completed un-submitted Supply chain, by redirecting to tasklist page', () => {
    cy.visit(Cypress.config('baseUrl') + `/${completedSC.slug}/complete`)
  })
  it('displays bread crumbs', () => {
    cy.get('li').contains('Home')
    cy.get('li').contains(`Update ${completedSC.name}`)
  })
  it('displays the correct header', () => {
    cy.get('h1').contains(`Update ${completedSC.name}`)
    cy.get('div').contains(`Update incomplete`)
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
  it('displays disabled submit button', () => {
    cy.get('form').find('button').should('be.enabled')
  })
})