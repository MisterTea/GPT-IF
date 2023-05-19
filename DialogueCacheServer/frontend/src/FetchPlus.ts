const fetchPlus = (url: string, options = {}, retries: number): Promise<any> =>
  fetch(url, options)
    .then(res => {
      if (res.ok) {
        return res.json();
      }
      if (retries > 0) {
        return fetchPlus(url, options, retries - 1);
      }
      throw new Error(res.status.toString());
    })
    .catch(error => {
      throw error;
    });

    export default fetchPlus;
