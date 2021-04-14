import users from '../fixtures/user.json'
import govDepartments from '../fixtures/govDepartment.json'
import supplyChains from '../fixtures/supplyChains.json'


const user = users[0].fields
const govDepartment = govDepartments[0].fields
const supplyChain = supplyChains[4].fields

describe('The Supply Chain Tasklist Page', () => {
  it('successfully loads', () => {
    // cy.visit(Cypress.config('baseUrl') + `/${supplyChain.slug}`)
    cy.visit(Cypress.config('baseUrl'))
  })
  it("displays user's name and department in header", () => {
    cy.get('.app-header-item').should(
      'have.text',
      `${user.first_name} ${user.last_name} - ${govDepartment.name}`
    )
  })
})
