import users from '../fixtures/user.json'
import govDepartments from '../fixtures/govDepartment.json'
import supplyChains from '../fixtures/supplyChains.json'
import { urlBuilder } from "../support/utils.js"

const adminUser = users[0].fields
const govDepartment = govDepartments[0].fields
const supplyChain = supplyChains[0]
const urls = urlBuilder(supplyChain);


describe('The SAP filters page for admin user', () => {
  it('successfully loads', () => {
    cy.visit(urls.sap)
    cy.injectAxe()
  })
  it('has no accessibility issues', () => {
    cy.runA11y()
  })
  it("displays user's name and department in header", () => {
    cy.get('.app-header-item').should(
      'have.text',
      `${adminUser.first_name} ${adminUser.last_name} - ${govDepartment.name}`
    )
  })
  it('displays the correct header', () => {
    cy.get('h1').contains(`Strategic action progress`)
    cy.get('p').contains(`Apply filters to see strategic action progress`)
  })
  it('displays drop down for department and supply chains', () => {
    cy.get('div > label').contains('Department')
    cy.get('div > label').contains('Supply chain')
    cy.get('div > select').should('have.length', 2)
  })
  it('displays enabled filter buttons', () => {
    cy.get('button').contains('Apply filters')
    cy.get('a').contains('Remove filters')
  })
  it('can select department', () => {
    cy.get('div > #id_department').select(`${govDepartment.name}`)
    cy.url().should('eq', urls.sap + `${govDepartment.name}/`)
  })
  it('can change department and bring back', () => {
    const otherDept = govDepartments[1].fields
    cy.get('div > #id_department').select(`${otherDept.name}`)
    cy.url().should('match', /.*department/)

    cy.get('div > #id_department').select(`${govDepartment.name}`)
    cy.url().should('eq', urls.sap + `${govDepartment.name}/`)
  })
  it('can views supply chains', () => {
    cy.get('div > #id_supply_chain > option').should('have.length', 12)

  })
  it('can select supply chain and submit', () => {
    const successUrl = urls.sap + `${govDepartment.name}/` + `${supplyChain.fields.slug}/`
    cy.get('div > #id_supply_chain').select(`${supplyChain.fields.name}`)
    cy.url().should('not.eq', successUrl)
    cy.get('button').contains('Apply filters').click()
    cy.url().should('eq', successUrl)
  })
  it('can reset filters', () => {
    cy.get('a').contains('Remove filters').click()
    cy.url().should('eq', urls.sap)
  })
})

describe('Error handling of SAP filter page', () => {
  it('successfully loads', () => {
    cy.visit(urls.sap)
  })
  it('trigger error by empty form submittion', () => {
    cy.get('button').contains('Apply filters').click()
    cy.url().should('eq', urls.sap)
    cy.get('#error-summary-title').contains('There is a problem')
    cy.get('li')
      .find('a')
      .contains('You must select a department to continue')
      .should('have.attr', 'href')
      .and('equal', '#id_department')
  })
  it('trigger supply chain error ', () => {
    const deptPostRoute = urls.sap + `${govDepartment.name}/`
    cy.get('div > #id_department').select(`${govDepartment.name}`)
    cy.url().should('eq', deptPostRoute)
    cy.get('button').contains('Apply filters').click()
    cy.url().should('eq', deptPostRoute )
    cy.get('#error-summary-title').contains('There is a problem')
    cy.get('li')
      .find('a')
      .contains('You must select a supply chain to continue')
      .should('have.attr', 'href')
      .and('equal', '#id_supply_chain')
  })
})

