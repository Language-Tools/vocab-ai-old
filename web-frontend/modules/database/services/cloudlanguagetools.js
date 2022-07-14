export default (client) => {
  return {
    fetchAllLanguages() {
      return client.get(`/database/cloudlanguagetools/language_list`)
    },
  }
}
