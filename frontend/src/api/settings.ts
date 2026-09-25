export type UpdateStatus = {
	update_available: boolean;
	current_version: string;
	latest_version: string;
};

export type UpdateStartResponse = {
	status: string;
};

async function parseError(response: Response): Promise<never> {
	let detail = `Request failed: ${response.status}`;

	try {
		const body = await response.json();
		if (typeof body.detail === "string") {
			detail = body.detail;
		}
	} catch {
		// Keep the HTTP status when the response has no JSON body.
	}

	throw new Error(detail);
}

export async function checkUpdates(): Promise<UpdateStatus> {
	const response = await fetch("/api/checkUpdates");

	if (!response.ok) {
		return parseError(response);
	}

	return response.json();
}

export async function startUpdate(): Promise<UpdateStartResponse> {
	const response = await fetch("/api/update", {
		method: "POST",
	});

	if (!response.ok) {
		return parseError(response);
	}

	return response.json();
}
