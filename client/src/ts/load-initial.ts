type ElementMap = { [key: string]: HTMLElement[] };
interface AjaxResponse<T> {
    isJson: boolean;
    content: T;
}

interface InitialDataOptions {
    onLoad?: string;
}

export const loadInitialAsync = async (): Promise<void> => {
    const initials = Array.from(document.querySelectorAll<HTMLElement>('[data-initial]'))
        // group by data-initial
        .reduce((acc, value) => {
            // we know based on the query selector above, that this is a safe assertion.
            // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
            const url = value.dataset.initial!;
            acc[url] = [...(acc[url] ?? []), value];
            return acc;
        }, <ElementMap>{});

    const promises = Object.entries(initials).map(async ([url, elms]) => {
        const response = await fetch(url, {
            headers: {
                // need so django interprets this as an AJAX request
                'X-Requested-With': 'XMLHttpRequest',
            },
        });

        // TODO handle error
        if (!response.ok) throw `${response.status}: ${response.statusText}`;

        const data = await (<Promise<AjaxResponse<string>>>response.json());
        elms.forEach((elm) => {
            const { onLoad } = <InitialDataOptions>elm.dataset;
            if (onLoad) {
                const loadFunc = eval(onLoad);
                loadFunc(data);
            } else if (!data.isJson) elm.innerHTML = data.content;
            else throw 'the loaded data was json, but no onLoad method was provided';
        });
    });

    await Promise.all(promises);
};
